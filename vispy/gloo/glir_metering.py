# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Per-frame metering of vispy GLIR texture uploads.

vispy drains its entire GLIR command queue inside whichever draw happens
next — including interaction frames. With progressive loading, dozens of
megabytes of ``glTexSubImage3D`` traffic can accumulate between draws and
the drain then blocks the main thread for hundreds of milliseconds to
seconds (macOS GL-over-Metal is the worst case: ~125 MB/s effective with
multi-second outliers for large single uploads).

When enabled, VisPy's GLIR queue dispatches through this module so that

- a single large texture ``DATA`` command is split into small slab
  sub-uploads (contiguous views along the leading axes, no copies), and
- each frame spends at most ``frame_budget_bytes`` on texture uploads;
  the remainder is carried to the *next* frame and a redraw is scheduled
  so the carry keeps draining even without interaction.

GLIR ordering semantics are preserved per object: once a command for a
texture is deferred, every later command for that same texture id is
deferred behind it. ``SIZE`` (re-specification) and ``DELETE`` commands
cancel any earlier carried uploads for their id, mirroring vispy's own
queue filtering.

Metering is opt-in through :func:`install`; the default GLIR behavior is
unchanged.

Examples
--------
Enable a 4 MiB per-frame budget with 1 MiB upload slabs::

    from vispy.gloo import glir_metering

    glir_metering.install(
        frame_budget_bytes=4 * 2**20,
        slab_bytes=1 * 2**20,
    )

Run ``python -m vispy.gloo.glir_metering`` for a standalone
vispy-only benchmark of draw time vs. texture upload size,
with and without metering.
"""

from __future__ import annotations

import contextlib
import logging
import time
import weakref

import numpy as np

LOGGER = logging.getLogger(__name__)

__all__ = [
    'DEFAULT_FRAME_BUDGET_BYTES',
    'DEFAULT_SLAB_BYTES',
    'add_drain_callback',
    'add_unmetered_texture',
    'discard_unmetered_texture',
    'hold_uploads_until',
    'install',
    'is_installed',
    'pending_upload_bytes',
    'remove_drain_callback',
    'uninstall',
]

_FACTORY_FRAME_BUDGET_BYTES = 4 * 2**20
_FACTORY_SLAB_BYTES = 1 * 2**20
DEFAULT_FRAME_BUDGET_BYTES = _FACTORY_FRAME_BUDGET_BYTES
DEFAULT_SLAB_BYTES = _FACTORY_SLAB_BYTES
#: Deferred GL object deletions executed per quiet flush. Deletion can
#: sync the GPU pipeline, so the backlog drains a few per frame instead
#: of all at once.
DELETE_DRAIN_PER_FLUSH = 4
#: 2D texture DATA at or above this size is metered like 3D uploads.
#: Small 2D textures (colormap LUTs, interpolation kernels) MUST stay
#: synchronous: deferring them leaves a shader sampling an unwritten
#: texture for however long the carry takes to drain.
TEX2D_MIN_METERED_BYTES = 256 * 1024

# Commands that operate on a specific GLIR object id and therefore must
# stay ordered behind any deferred command for the same id.
_OBJECT_COMMANDS = frozenset(
    {'DATA', 'SIZE', 'WRAPPING', 'INTERPOLATION', 'DELETE'},
)

# GL state setters that are idempotent: re-issuing the same call with
# the same arguments is semantically a no-op, but on a busy GPU each
# call can block on pipeline synchronization (profiled at ~6ms average
# on macOS GL-over-Metal; 271 calls cost 1.6s in one short session).
# Consecutive duplicates are skipped. glEnable/glDisable are handled
# per capability. Deliberately NOT listed: glClear*, glViewport,
# glScissor, glFinish, glFlush (must always run or are
# framebuffer-dependent).
_IDEMPOTENT_FUNCS = frozenset(
    {
        'glBlendFunc',
        'glBlendFuncSeparate',
        'glBlendEquation',
        'glBlendEquationSeparate',
        'glBlendColor',
        'glDepthFunc',
        'glDepthMask',
        'glDepthRange',
        'glCullFace',
        'glFrontFace',
        'glLineWidth',
        'glPolygonOffset',
        'glColorMask',
        'glStencilFunc',
        'glStencilFuncSeparate',
        'glStencilMask',
        'glStencilMaskSeparate',
        'glStencilOp',
        'glStencilOpSeparate',
        'glHint',
        'glSampleCoverage',
        # value-state setters: global GL state, idempotent by args.
        # glClear itself must always run and is never cached.
        'glViewport',
        'glScissor',
        'glClearColor',
        'glClearDepth',
        'glClearStencil',
    }
)

_enabled = False
_hooked_canvases: weakref.WeakSet = weakref.WeakSet()
# while time.monotonic() < this, defer ALL metered texture uploads
# (interaction hold: see ProgressiveLoader._on_interaction)
_upload_hold_until = 0.0

# GLIR ids whose uploads are never metered. Double-buffered textures
# register here: their writes always target an unbound texture and the
# swap that makes them visible is atomic — deferring those uploads
# would present a partially written texture (a black flash), the exact
# artifact the buffering exists to prevent.
_unmetered_ids: set = set()


def add_unmetered_texture(glir_id) -> None:
    """Exempt a texture's GLIR id from upload metering."""
    _unmetered_ids.add(glir_id)


def discard_unmetered_texture(glir_id) -> None:
    """Remove a previously registered exemption (id may be absent)."""
    _unmetered_ids.discard(glir_id)


# weak callbacks invoked (on the GL/main thread) when a parser's upload
# carry fully drains; used to restore interactive render LOD without a
# polling timer
_drain_callbacks: list = []


def add_drain_callback(method) -> None:
    """Register a bound method to call when an upload carry drains."""
    ref = weakref.WeakMethod(method)
    if all(ref != existing for existing in _drain_callbacks):
        _drain_callbacks.append(ref)


def remove_drain_callback(method) -> None:
    """Remove a previously registered drain callback."""
    _drain_callbacks[:] = [
        ref
        for ref in _drain_callbacks
        if (cb := ref()) is not None and cb != method
    ]


def _notify_drained() -> None:
    alive = []
    for ref in _drain_callbacks:
        cb = ref()
        if cb is None:
            continue
        alive.append(ref)
        try:
            cb()
        except Exception:  # pragma: no cover - callback bug
            LOGGER.warning('drain callback failed', exc_info=True)
    _drain_callbacks[:] = alive


def pending_upload_bytes() -> int:
    """Total bytes of carried (not yet executed) texture uploads.

    Lets callers couple behavior to the upload backlog — e.g. keep the
    interactive render LOD degraded until a level switch's full-tile
    upload has fully drained into the GPU.
    """
    return sum(
        sum(c[3].nbytes for c in state.carry if c[0] == 'DATA')
        for state in _states.values()
    )


def hold_uploads_until(deadline: float) -> None:
    """Defer all metered texture uploads until ``time.monotonic()`` >= deadline.

    Called on every interaction event; the deadline only ever extends.
    Carried uploads keep scheduling redraws, so draining resumes by
    itself once the hold expires.
    """
    global _upload_hold_until
    _upload_hold_until = max(_upload_hold_until, float(deadline))


class _ParserState:
    """Per-GlirParser metering state (carry survives across flushes)."""

    def __init__(self, frame_budget_bytes: int, slab_bytes: int):
        self.frame_budget = int(frame_budget_bytes)
        self.slab_bytes = min(int(slab_bytes), self.frame_budget)
        self.budget_left = self.frame_budget
        self.carry: list[tuple] = []
        self.last_reset = time.perf_counter()
        # last-applied GL state for the redundant-FUNC filter; cleared
        # whenever the context is made current
        self.gl_state: dict = {}
        # DELETE commands held until a quiet flush: each delete
        # synchronizes with pending GPU work (~25ms profiled), so they
        # run only in flushes with no uploads and no interaction hold.
        # Safe to defer arbitrarily: GLIR ids are never reused.
        self.deferred_deletes: list[tuple] = []
        # ids whose deferred DELETE has executed. Deferral reorders
        # deletes past later flushes, so commands for these ids can
        # still arrive (e.g. from another canvas's queue on a shared
        # context) — they are void and must be dropped, exactly as an
        # inline delete would have voided them. Ids are never reused,
        # so membership stays valid for the parser's lifetime.
        self.dead_ids: set = set()
        # whether the current flush executed any metered DATA command;
        # drives drain notification for uploads small enough to never
        # have been carried
        self.executed_metered = False

    def reset_budget(self):
        self.budget_left = self.frame_budget
        self.last_reset = time.perf_counter()


# keyed by GlirParser so canvases sharing a context share one budget
_states: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()


def _state_for(parser) -> _ParserState:
    state = _states.get(parser)
    if state is None:
        # read the module globals at call time: install() retunes them
        state = _ParserState(DEFAULT_FRAME_BUDGET_BYTES, DEFAULT_SLAB_BYTES)
        _states[parser] = state
    return state


def _is_metered_texture(ob, data=None) -> bool:
    """Whether uploads to this GLIR object count against the budget.

    All 3D textures are metered (the pathological path on macOS). 2D
    textures are metered only for payloads of at least
    ``TEX2D_MIN_METERED_BYTES`` — image tiles, not colormap LUTs or
    interpolation kernels, which must upload synchronously so shaders
    never sample an unwritten texture.
    """
    from vispy.gloo import glir

    if isinstance(ob, glir.GlirTexture3D):
        return True
    return (
        TEX2D_MIN_METERED_BYTES > 0
        and isinstance(ob, glir.GlirTexture2D)
        and data is not None
        and getattr(data, 'nbytes', 0) >= TEX2D_MIN_METERED_BYTES
    )


def _split_slabs(offset, data, slab_bytes):
    """Split a texture DATA payload into <= slab_bytes sub-uploads.

    Splits along the leading texel axis first (contiguous views of a
    C-contiguous source), recursing into the second axis when a single
    leading slice is itself too large. Yields ``(offset, subarray)``.
    """
    if data.nbytes <= slab_bytes or data.ndim < 2 or data.shape[0] == 0:
        yield tuple(offset), data
        return
    bytes_per_slice = data.nbytes // data.shape[0]
    step = max(1, int(slab_bytes // max(1, bytes_per_slice)))
    for start in range(0, data.shape[0], step):
        sub = data[start:start + step]
        sub_offset = list(offset)
        sub_offset[0] += start
        if sub.nbytes > slab_bytes and sub.shape[0] == 1 and sub.ndim >= 3:
            # one leading slice is still too big: split its rows
            for in_off, in_sub in _split_slabs(
                offset=list(sub_offset[1:]),
                data=sub[0],
                slab_bytes=slab_bytes,
            ):
                yield (sub_offset[0], *in_off), in_sub[np.newaxis]
        else:
            yield tuple(sub_offset), sub


def _drop_deleted_carry(carry, new_commands):
    """Drop carried uploads whose texture is deleted in this flush.

    The carry only ever holds commands for metered textures, so this
    cannot affect other object types (notably shaders, whose DATA must
    survive even though vispy DELETEs them right after LINK).
    """
    deleted = {c[1] for c in new_commands if c[0] == 'DELETE'}
    if not deleted:
        return carry
    return [c for c in carry if c[1] not in deleted]


def _metered_parse(parser, commands, state, force_defer=False):
    """Execute commands under the upload budget; return the leftovers.

    With ``force_defer`` every metered texture upload is deferred
    regardless of budget (interaction hold); other commands still run.
    """
    # mirror GlirParser.parse's deferred deletion bookkeeping, which we
    # bypass by calling _parse directly
    from vispy.gloo.glir import JUST_DELETED

    for id_ in [
        id_ for id_, val in parser._objects.items() if val == JUST_DELETED
    ]:
        parser._objects.pop(id_)

    deferred_ids = set()
    leftover = []
    gl_state = state.gl_state
    for command in commands:
        cmd = command[0]
        id_ = command[1] if len(command) > 1 else None
        if id_ in deferred_ids and cmd in _OBJECT_COMMANDS:
            leftover.append(command)
            continue
        if cmd == 'FUNC':
            # skip GL state calls that match the last-applied state: on
            # a busy GPU even redundant glEnable/glBlendFunc calls
            # block on pipeline sync
            if id_ in ('glEnable', 'glDisable') and len(command) == 3:
                key = ('cap', command[2])
                if gl_state.get(key) == id_:
                    continue
                gl_state[key] = id_
            elif id_ in _IDEMPOTENT_FUNCS:
                key = ('fn', id_)
                if gl_state.get(key) == command[2:]:
                    continue
                gl_state[key] = command[2:]
        elif cmd == 'CURRENT':
            # context switch: cached GL state is no longer trustworthy
            gl_state.clear()
        elif cmd == 'DELETE':
            # run deletes only in quiet flushes (see _ParserState):
            # ordering is safe because anything queued for this id
            # earlier either already executed or was dropped with it
            state.deferred_deletes.append(command)
            continue
        if cmd == 'DATA':
            ob = parser._objects.get(id_, None)
            if id_ not in _unmetered_ids and _is_metered_texture(
                ob,
                command[3],
            ):
                offset, data = command[2], command[3]
                executed_any = False
                for sub_offset, sub in _split_slabs(
                    offset,
                    data,
                    state.slab_bytes,
                ):
                    # always make progress: with a full budget, upload at
                    # least one slab even if it alone exceeds the budget
                    fresh = state.budget_left >= state.frame_budget
                    if (
                        force_defer
                        or state.budget_left <= 0
                        or (
                            sub.nbytes > state.budget_left
                            and not (fresh and not executed_any)
                        )
                    ):
                        deferred_ids.add(id_)
                        leftover.append(('DATA', id_, sub_offset, sub))
                        continue
                    if not sub.flags['C_CONTIGUOUS']:
                        sub = np.ascontiguousarray(sub)
                    parser._parse(('DATA', id_, sub_offset, sub))
                    state.budget_left -= sub.nbytes
                    executed_any = True
                    state.executed_metered = True
                continue
        try:
            parser._parse(command)
        except RuntimeError as exc:
            if 'does not exist' not in str(exc):
                raise
            # the deferred DELETE drain reorders deletes past later
            # flushes, so a command can arrive for an object that no
            # longer exists (or does not exist YET, when its CREATE
            # sits in another queue of a shared context)
            if id_ in state.dead_ids:
                continue  # deleted: the command is void, drop it
            # not created yet: keep it (and everything ordered behind
            # it) in the carry until its CREATE arrives
            LOGGER.debug('deferring %s for missing object %s', cmd, id_)
            deferred_ids.add(id_)
            leftover.append(command)
    return leftover


def _attach_reset_hook(canvas):
    """Reset the upload budget at the start of each canvas draw."""
    if canvas is None or canvas in _hooked_canvases:
        return
    canvas_ref = weakref.ref(canvas)

    def _on_draw(event=None):
        if not _enabled:
            return
        c = canvas_ref()
        if c is None:
            return
        try:
            parser = c.context.shared.parser
        except (AttributeError, RuntimeError):
            return
        _state_for(parser).reset_budget()

    # position='first': run before the scene draw issues any flushes
    try:
        canvas.events.draw.connect(_on_draw, position='first')
    except RuntimeError:
        return
    _hooked_canvases.add(canvas)


def _flush(queue, parser):
    """Flush a GLIR queue with per-frame upload metering."""
    from vispy.gloo.context import get_current_canvas

    if queue._verbose:
        show = queue._verbose if isinstance(queue._verbose, str) else None
        queue.show(show)

    state = _state_for(parser)
    canvas = get_current_canvas()
    _attach_reset_hook(canvas)
    # fallback when no canvas draw hook fires (offscreen / bare gloo):
    # never let the carry starve for more than 0.25 s
    if (
        state.budget_left < state.frame_budget
        and time.perf_counter() - state.last_reset > 0.25
    ):
        state.reset_budget()

    carry, state.carry = state.carry, []
    new_commands = queue.clear()
    carry = _drop_deleted_carry(carry, new_commands)
    commands = queue._filter(carry + new_commands, parser)
    holding = time.monotonic() < _upload_hold_until
    had_carry = bool(carry)
    state.executed_metered = False
    state.carry = _metered_parse(parser, commands, state, force_defer=holding)

    if state.carry and canvas is not None:
        with contextlib.suppress(RuntimeError):
            canvas.update()
    elif (had_carry or state.executed_metered) and not state.carry:
        # notify on any flush that landed metered uploads and ended
        # clean — not only when a carry drained: uploads small enough
        # to fit one frame budget are never carried, but a present
        # (texture swap) may still be waiting on them
        _notify_drained()

    if (
        state.deferred_deletes
        and not holding
        and not state.carry
        and state.budget_left >= state.frame_budget
    ):
        # a quiet flush (no uploads this frame, no interaction): run
        # held GL object deletions now, off the busy periods. PACED:
        # each delete can sync the GPU pipeline (~10-25ms on busy macOS
        # GL-over-Metal), so draining hundreds in one flush is itself a
        # multi-second stall — exactly at pass end, when the queue is
        # deepest. The remainder drains over subsequent redraws.
        n = DELETE_DRAIN_PER_FLUSH
        deletes = state.deferred_deletes[:n]
        state.deferred_deletes = state.deferred_deletes[n:]
        for command in deletes:
            parser._parse(command)
            state.dead_ids.add(command[1])
        if state.deferred_deletes and canvas is not None:
            with contextlib.suppress(RuntimeError):
                canvas.update()


def install(
    frame_budget_bytes: int | None = None,
    slab_bytes: int | None = None,
) -> bool:
    """Enable GLIR texture-upload metering (idempotent).

    Returns True if metering is active after the call.
    """
    global _enabled, DEFAULT_FRAME_BUDGET_BYTES, DEFAULT_SLAB_BYTES

    frame_budget_bytes = int(
        DEFAULT_FRAME_BUDGET_BYTES
        if frame_budget_bytes is None
        else frame_budget_bytes
    )
    slab_bytes = int(DEFAULT_SLAB_BYTES if slab_bytes is None else slab_bytes)
    if frame_budget_bytes <= 0:
        raise ValueError('frame_budget_bytes must be positive')
    if slab_bytes <= 0:
        raise ValueError('slab_bytes must be positive')

    # re-parameterize existing states (and set defaults for new ones)
    DEFAULT_FRAME_BUDGET_BYTES = frame_budget_bytes
    DEFAULT_SLAB_BYTES = slab_bytes
    for state in _states.values():
        state.frame_budget = frame_budget_bytes
        state.slab_bytes = min(slab_bytes, frame_budget_bytes)

    if not _enabled:
        _enabled = True
        LOGGER.info(
            'GLIR texture upload metering enabled '
            '(budget=%d B/frame, slab=%d B)',
            frame_budget_bytes,
            slab_bytes,
        )
    return True


def uninstall():
    """Disable metering and synchronously flush deferred commands."""
    global _enabled, DEFAULT_FRAME_BUDGET_BYTES, DEFAULT_SLAB_BYTES
    DEFAULT_FRAME_BUDGET_BYTES = _FACTORY_FRAME_BUDGET_BYTES
    DEFAULT_SLAB_BYTES = _FACTORY_SLAB_BYTES
    if not _enabled:
        return
    _enabled = False
    # re-queue carried uploads and held deletions so they are not lost
    for parser, state in list(_states.items()):
        if state.carry:
            commands, state.carry = state.carry, []
            parser.parse(commands)
        if state.deferred_deletes:
            commands, state.deferred_deletes = state.deferred_deletes, []
            parser.parse(commands)
    _states.clear()


def is_installed() -> bool:
    return _enabled


def _benchmark():  # pragma: no cover - manual profiling tool
    """Pure-vispy benchmark: draw time vs. 3D texture upload size.

    Renders a vispy Volume and times the draw immediately after
    ``set_data`` calls of increasing size, with metering off and on.
    This is the minimal repro for the macOS GL-over-Metal upload stalls
    (run on Apple Silicon and compare the two curves).
    """
    import argparse

    parser_ = argparse.ArgumentParser(description=__doc__)
    parser_.add_argument('--size', type=int, default=512, help='volume edge')
    parser_.add_argument('--repeats', type=int, default=5)
    parser_.add_argument(
        '--budget',
        type=int,
        default=DEFAULT_FRAME_BUDGET_BYTES,
    )
    parser_.add_argument('--slab', type=int, default=DEFAULT_SLAB_BYTES)
    args = parser_.parse_args()

    from vispy import app, scene

    canvas = scene.SceneCanvas(keys=None, size=(800, 600), show=True)
    view = canvas.central_widget.add_view()
    n = args.size
    rng = np.random.default_rng(0)
    base = rng.random((n, n, n), dtype=np.float32)
    volume = scene.visuals.Volume(base, parent=view.scene)
    view.camera = scene.cameras.TurntableCamera(parent=view.scene, fov=60.0)

    def timed_draw():
        t0 = time.perf_counter()
        canvas.render()  # forces a full draw + flush
        return time.perf_counter() - t0

    sub_mb_sizes = [1, 2, 4, 8, 16, 32, 64]
    for label, metered in (('unmetered', False), ('metered', True)):
        if metered:
            install(frame_budget_bytes=args.budget, slab_bytes=args.slab)
        else:
            uninstall()
        # warm up
        for _ in range(3):
            timed_draw()
        print(f'--- {label} ---')  # noqa: T201
        for mb in sub_mb_sizes:
            nz = max(1, int(mb * 2**20 // (n * n * base.itemsize)))
            if nz > n:
                break
            sub = rng.random((nz, n, n), dtype=np.float32)
            times = []
            for i in range(args.repeats):
                z = (i * nz) % max(1, n - nz)
                t0 = time.perf_counter()
                volume._texture.set_data(sub, offset=(z, 0, 0))
                t_set = time.perf_counter() - t0
                t_draw = timed_draw()
                # with metering, drain the carry and count total time.
                # canvas.render() bypasses the draw event, so emulate the
                # per-frame budget reset a real paint event would trigger.
                t_drain = 0.0
                if metered:
                    while _states and any(s.carry for s in _states.values()):
                        for s in _states.values():
                            s.reset_budget()
                        t_drain += timed_draw()
                times.append((t_set, t_draw, t_drain))
            worst = max(t[1] for t in times)
            total = max(t[1] + t[2] for t in times)
            print(  # noqa: T201
                f'{mb:>4} MB sub-upload: worst single draw '
                f'{worst * 1e3:7.1f} ms, total incl. drain '
                f'{total * 1e3:7.1f} ms',
            )
    app.process_events()
    canvas.close()


if __name__ == '__main__':  # pragma: no cover
    _benchmark()
