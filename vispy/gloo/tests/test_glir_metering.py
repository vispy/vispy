# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Tests for per-frame GLIR texture upload metering.

These run without a GL context: a fake parser records what would be
executed and real ``GlirTexture3D`` instances are created via ``__new__``
(no GL calls) purely so isinstance checks pass.
"""

import numpy as np
import pytest
from vispy.gloo import glir

from vispy.gloo import glir_metering as gm


class FakeParser:
    """Records parsed commands instead of touching GL."""

    supports_texture_upload_metering = True

    def __init__(self):
        self._objects = {}
        self.executed = []

    def add_texture3d(self, id_):
        tex = glir.GlirTexture3D.__new__(glir.GlirTexture3D)
        self._objects[id_] = tex
        return tex

    def add_texture2d(self, id_):
        tex = glir.GlirTexture2D.__new__(glir.GlirTexture2D)
        self._objects[id_] = tex
        return tex

    def _parse(self, command):
        self.executed.append(command)

    def parse(self, commands):
        for c in commands:
            self._parse(c)


@pytest.fixture
def parser():
    return FakeParser()


def make_state(budget, slab):
    return gm._ParserState(frame_budget_bytes=budget, slab_bytes=slab)


def data_bytes(commands):
    return sum(c[3].nbytes for c in commands if c[0] == 'DATA')


def test_small_commands_pass_through_in_order(parser):
    parser.add_texture3d(1)
    state = make_state(budget=2**20, slab=2**20)
    small = np.zeros((4, 4, 4), dtype=np.uint8)
    commands = [
        ('UNIFORM', 7, 'u_x', 'float', 1.0),
        ('DATA', 1, (0, 0, 0), small),
        ('DRAW', 7, 'triangles', None, 1),
    ]
    leftover = gm._metered_parse(parser, commands, state)
    assert leftover == []
    assert [c[0] for c in parser.executed] == ['UNIFORM', 'DATA', 'DRAW']


def test_large_data_split_into_slabs(parser):
    parser.add_texture3d(1)
    # 64 z-slices of 64 KiB each = 4 MiB total, 256 KiB slabs
    data = (
        np.arange(64 * 256 * 256, dtype=np.uint8)
        .reshape(64, 256, 256)
        .copy()  # own the buffer so the .base view check below holds
    )
    state = make_state(budget=64 * 2**20, slab=256 * 2**10)
    leftover = gm._metered_parse(parser, [('DATA', 1, (8, 0, 0), data)], state)
    assert leftover == []
    executed = parser.executed
    assert all(c[0] == 'DATA' for c in executed)
    assert len(executed) == 16  # 4 MiB / 256 KiB
    # offsets advance along z from the original offset
    assert [c[2][0] for c in executed] == [8 + 4 * i for i in range(16)]
    assert all(c[2][1:] == (0, 0) for c in executed)
    # reassembly reproduces the original payload
    reassembled = np.concatenate([c[3] for c in executed], axis=0)
    np.testing.assert_array_equal(reassembled, data)
    # slabs are views, not copies
    assert all(c[3].base is data for c in executed)


def test_single_slice_too_large_splits_rows(parser):
    parser.add_texture3d(1)
    # one z-slice of 1 MiB with a 256 KiB slab limit -> split along y
    data = np.zeros((1, 1024, 1024), dtype=np.uint8)
    state = make_state(budget=64 * 2**20, slab=256 * 2**10)
    leftover = gm._metered_parse(parser, [('DATA', 1, (3, 0, 0), data)], state)
    assert leftover == []
    assert len(parser.executed) == 4
    assert [c[2] for c in parser.executed] == [
        (3, 256 * i, 0) for i in range(4)
    ]
    assert all(c[3].shape == (1, 256, 1024) for c in parser.executed)


def test_budget_defers_remainder(parser):
    parser.add_texture3d(1)
    data = np.zeros((16, 256, 256), dtype=np.uint8)  # 1 MiB
    state = make_state(budget=512 * 2**10, slab=128 * 2**10)
    leftover = gm._metered_parse(parser, [('DATA', 1, (0, 0, 0), data)], state)
    assert data_bytes(parser.executed) == 512 * 2**10
    assert data_bytes(leftover) == 512 * 2**10
    assert state.budget_left == 0
    # next frame: fresh budget drains the carry
    state.reset_budget()
    leftover2 = gm._metered_parse(parser, leftover, state)
    assert leftover2 == []
    assert data_bytes(parser.executed) == data.nbytes


def test_non_texture_commands_run_past_deferred_uploads(parser):
    parser.add_texture3d(1)
    data = np.zeros((16, 256, 256), dtype=np.uint8)  # 1 MiB
    state = make_state(budget=256 * 2**10, slab=256 * 2**10)
    commands = [
        ('DATA', 1, (0, 0, 0), data),
        ('UNIFORM', 7, 'u_x', 'float', 1.0),
        ('DRAW', 7, 'triangles', None, 1),
        # but same-id commands stay ordered behind the deferred upload
        ('WRAPPING', 1, ('clamp_to_edge',) * 3),
    ]
    leftover = gm._metered_parse(parser, commands, state)
    executed_kinds = [c[0] for c in parser.executed]
    assert 'UNIFORM' in executed_kinds
    assert 'DRAW' in executed_kinds
    assert 'WRAPPING' not in executed_kinds
    assert leftover[-1][0] == 'WRAPPING'
    assert all(c[0] == 'DATA' for c in leftover[:-1])


def test_oversized_single_slab_still_makes_progress(parser):
    parser.add_texture3d(1)
    # a slab that alone exceeds the whole budget: with a fresh budget it
    # must execute anyway, otherwise the carry never drains
    data = np.zeros((1, 64, 64), dtype=np.uint8)
    state = make_state(budget=1024, slab=1024)
    state.slab_bytes = data.nbytes  # force a single indivisible slab
    leftover = gm._metered_parse(parser, [('DATA', 1, (0, 0, 0), data)], state)
    assert leftover == []
    assert data_bytes(parser.executed) == data.nbytes


def test_delete_drops_carried_uploads():
    data = np.zeros((4, 4, 4), dtype=np.uint8)
    carry = [
        ('DATA', 1, (0, 0, 0), data),
        ('DATA', 2, (0, 0, 0), data),
    ]
    new_commands = [
        ('DELETE', 1),
        # shader-style DATA-then-DELETE in the new commands must be
        # left alone (vispy deletes shaders right after LINK)
        ('DATA', 3, 0, 'shader code'),
        ('DELETE', 3),
    ]
    out = gm._drop_deleted_carry(carry, new_commands)
    assert out == [('DATA', 2, (0, 0, 0), data)]
    assert new_commands == [
        ('DELETE', 1),
        ('DATA', 3, 0, 'shader code'),
        ('DELETE', 3),
    ]


def test_unknown_object_data_unmetered(parser):
    # DATA for buffers/shaders (not metered textures) passes through
    state = make_state(budget=1, slab=1)
    big = np.zeros((1024, 1024), dtype=np.float32)
    leftover = gm._metered_parse(parser, [('DATA', 99, 0, big)], state)
    assert leftover == []
    assert parser.executed == [('DATA', 99, 0, big)]


def test_large_2d_texture_metered(parser):
    parser.add_texture2d(1)
    # 4 MiB image upload, 256 KiB slabs, 1 MiB budget: 4 slabs run,
    # the rest carries to the next frame
    data = np.zeros((1024, 4096), dtype=np.uint8)
    state = make_state(budget=2**20, slab=256 * 2**10)
    leftover = gm._metered_parse(parser, [('DATA', 1, (0, 0), data)], state)
    assert data_bytes(parser.executed) == 2**20
    assert data_bytes(leftover) == data.nbytes - 2**20
    # offsets advance along rows
    assert [c[2][0] for c in parser.executed] == [64 * i for i in range(4)]


def test_small_2d_texture_not_metered(parser):
    # colormap-LUT-sized uploads must run synchronously even with an
    # exhausted budget: a deferred LUT leaves the shader sampling an
    # unwritten texture
    parser.add_texture2d(1)
    state = make_state(budget=2**20, slab=256 * 2**10)
    state.budget_left = 0
    lut = np.zeros((256, 4), dtype=np.float32)  # 4 KiB
    leftover = gm._metered_parse(parser, [('DATA', 1, (0, 0), lut)], state)
    assert leftover == []
    assert parser.executed == [('DATA', 1, (0, 0), lut)]


def test_install_uninstall_idempotent():
    # Metering is dispatched natively by the queue, so enabling it does
    # not replace the flush method.
    gm.uninstall()
    original = glir._GlirQueueShare.flush
    try:
        assert gm.install()
        assert gm.is_installed()
        assert gm.install()  # second install is a no-op
        assert glir._GlirQueueShare.flush is original
    finally:
        gm.uninstall()
    assert glir._GlirQueueShare.flush is original
    assert not gm.is_installed()
    gm.uninstall()  # second uninstall is a no-op


def test_install_rejects_nonpositive_limits():
    with pytest.raises(ValueError, match='frame_budget_bytes'):
        gm.install(frame_budget_bytes=0)
    with pytest.raises(ValueError, match='slab_bytes'):
        gm.install(slab_bytes=-1)


def test_remote_parser_uses_default_flush():
    class RemoteParser:
        supports_texture_upload_metering = False

        def __init__(self):
            self.commands = []

        def parse(self, commands):
            self.commands.extend(commands)

    parser = RemoteParser()
    queue = glir.GlirQueue()
    queue.command('DATA', 1, 0, np.zeros(8, dtype=np.uint8))
    try:
        gm.install()
        queue.flush(parser)
    finally:
        gm.uninstall()
    assert len(parser.commands) == 1
    assert parser.commands[0][0] == 'DATA'


def test_metered_flush_carries_and_drains(monkeypatch):
    monkeypatch.setattr(
        'vispy.gloo.context.get_current_canvas',
        lambda: None,
    )
    parser = FakeParser()
    parser.add_texture3d(1)
    try:
        assert gm.install(
            frame_budget_bytes=512 * 2**10,
            slab_bytes=128 * 2**10,
        )
        queue = glir.GlirQueue()
        data = np.zeros((16, 256, 256), dtype=np.uint8)  # 1 MiB
        queue.command('DATA', 1, (0, 0, 0), data)
        queue.flush(parser)
        assert data_bytes(parser.executed) == 512 * 2**10
        state = gm._states[parser]
        assert data_bytes(state.carry) == 512 * 2**10
        # next frame: budget reset (simulating the canvas draw hook),
        # empty queue still drains the carry
        state.reset_budget()
        queue.flush(parser)
        assert data_bytes(parser.executed) == data.nbytes
        assert state.carry == []
    finally:
        gm.uninstall()


def test_metered_flush_new_size_cancels_carry(monkeypatch):
    monkeypatch.setattr(
        'vispy.gloo.context.get_current_canvas',
        lambda: None,
    )
    parser = FakeParser()
    parser.add_texture3d(1)
    try:
        assert gm.install(
            frame_budget_bytes=512 * 2**10,
            slab_bytes=128 * 2**10,
        )
        queue = glir.GlirQueue()
        data = np.zeros((16, 256, 256), dtype=np.uint8)  # 1 MiB
        queue.command('DATA', 1, (0, 0, 0), data)
        queue.flush(parser)
        state = gm._states[parser]
        assert state.carry
        # a SIZE re-specification supersedes the carried uploads
        state.reset_budget()
        small = np.zeros((4, 4, 4), dtype=np.uint8)
        queue.command('SIZE', 1, (4, 4, 4), 'luminance', None)
        queue.command('DATA', 1, (0, 0, 0), small)
        queue.flush(parser)
        assert state.carry == []
        kinds = [c[0] for c in parser.executed]
        assert kinds[-2:] == ['SIZE', 'DATA']
        assert parser.executed[-1][3] is small
        # none of the stale 1 MiB payload was uploaded after the SIZE
        assert data_bytes(parser.executed) == 512 * 2**10 + small.nbytes
    finally:
        gm.uninstall()


def test_redundant_gl_state_calls_skipped(parser):
    state = make_state(budget=2**20, slab=2**20)
    commands = [
        ('FUNC', 'glEnable', 'blend'),
        ('FUNC', 'glBlendFunc', 'src_alpha', 'one_minus_src_alpha'),
        ('FUNC', 'glEnable', 'blend'),  # duplicate: skipped
        ('FUNC', 'glBlendFunc', 'src_alpha', 'one_minus_src_alpha'),  # dup
        ('FUNC', 'glEnable', 'depth_test'),  # different capability: kept
        ('FUNC', 'glDisable', 'blend'),  # state transition: kept
        ('FUNC', 'glEnable', 'blend'),  # transition back: kept
        ('FUNC', 'glBlendFunc', 'one', 'one'),  # changed args: kept
        ('FUNC', 'glClear', 17664),  # never cached
        ('FUNC', 'glClear', 17664),
    ]
    leftover = gm._metered_parse(parser, commands, state)
    assert leftover == []
    executed = [c[1:] for c in parser.executed]
    assert executed == [
        ('glEnable', 'blend'),
        ('glBlendFunc', 'src_alpha', 'one_minus_src_alpha'),
        ('glEnable', 'depth_test'),
        ('glDisable', 'blend'),
        ('glEnable', 'blend'),
        ('glBlendFunc', 'one', 'one'),
        ('glClear', 17664),
        ('glClear', 17664),
    ]
    # the cache persists across flushes (GL state is per-context)
    leftover = gm._metered_parse(
        parser, [('FUNC', 'glBlendFunc', 'one', 'one')], state
    )
    assert leftover == []
    assert len(parser.executed) == 8


def test_viewport_and_clearcolor_deduped(parser):
    state = make_state(budget=2**20, slab=2**20)
    commands = [
        ('FUNC', 'glViewport', 0, 0, 800, 600),
        ('FUNC', 'glClearColor', 0.0, 0.0, 0.0, 1.0),
        ('FUNC', 'glViewport', 0, 0, 800, 600),  # duplicate: skipped
        ('FUNC', 'glClearColor', 0.0, 0.0, 0.0, 1.0),  # dup: skipped
        ('FUNC', 'glViewport', 0, 0, 400, 300),  # changed: kept
        ('FUNC', 'glViewport', 0, 0, 800, 600),  # changed back: kept
    ]
    leftover = gm._metered_parse(parser, commands, state)
    assert leftover == []
    assert [c[2:] for c in parser.executed if c[1] == 'glViewport'] == [
        (0, 0, 800, 600),
        (0, 0, 400, 300),
        (0, 0, 800, 600),
    ]
    assert len([c for c in parser.executed if c[1] == 'glClearColor']) == 1


def test_deletes_deferred_to_quiet_flush(monkeypatch):

    parser = FakeParser()
    parser.add_texture3d(1)
    try:
        assert gm.install(
            frame_budget_bytes=512 * 2**10, slab_bytes=128 * 2**10
        )
        queue = glir.GlirQueue()
        data = np.zeros((16, 256, 256), dtype=np.uint8)  # 1 MiB
        queue.command('DATA', 1, (0, 0, 0), data)
        queue.command('DELETE', 7)  # unrelated object
        queue.flush(parser)
        state = gm._states[parser]
        # busy flush (uploads executed, carry pending): delete held
        assert state.carry
        assert state.deferred_deletes == [('DELETE', 7)]
        assert all(c[0] != 'DELETE' for c in parser.executed)
        # drain the carry across quiet-less flushes
        state.reset_budget()
        queue.flush(parser)
        assert not state.carry
        # this flush still spent budget on uploads: delete still held
        assert state.deferred_deletes == [('DELETE', 7)]
        # a genuinely quiet flush executes it
        state.reset_budget()
        queue.flush(parser)
        assert state.deferred_deletes == []
        assert parser.executed[-1] == ('DELETE', 7)
    finally:
        gm.uninstall()


def test_delete_drain_is_paced(monkeypatch):
    """A big delete backlog drains a few per quiet flush, not all at
    once — each deletion can sync the GPU pipeline, so a bulk drain is
    itself a multi-second stall at pass end.
    """

    parser = FakeParser()
    parser.add_texture3d(1)
    try:
        assert gm.install(
            frame_budget_bytes=512 * 2**10, slab_bytes=128 * 2**10
        )
        queue = glir.GlirQueue()
        data = np.zeros((16, 256, 256), dtype=np.uint8)  # 1 MiB
        queue.command('DATA', 1, (0, 0, 0), data)
        n_deletes = gm.DELETE_DRAIN_PER_FLUSH * 2 + 3
        for i in range(n_deletes):
            queue.command('DELETE', 100 + i)
        queue.flush(parser)  # busy: uploads spent, deletes held
        state = gm._states[parser]
        assert len(state.deferred_deletes) == n_deletes
        # drain the upload carry
        while state.carry:
            state.reset_budget()
            queue.flush(parser)
        executed_deletes = lambda: sum(  # noqa: E731
            c[0] == 'DELETE' for c in parser.executed
        )
        before = executed_deletes()
        state.reset_budget()
        queue.flush(parser)  # quiet: paced batch only
        assert executed_deletes() - before == gm.DELETE_DRAIN_PER_FLUSH
        assert len(state.deferred_deletes) == (
            n_deletes - gm.DELETE_DRAIN_PER_FLUSH
        )
        # subsequent quiet flushes drain the rest
        for _ in range(3):
            state.reset_budget()
            queue.flush(parser)
        assert not state.deferred_deletes
        assert executed_deletes() == n_deletes
    finally:
        gm.uninstall()


def test_uninstall_flushes_deferred_deletes(monkeypatch):

    parser = FakeParser()
    try:
        assert gm.install()
        state = gm._state_for(parser)
        state.deferred_deletes.append(('DELETE', 3))
    finally:
        gm.uninstall()
    assert parser.executed == [('DELETE', 3)]


def test_glir_flush_never_exceeds_frame_budget(monkeypatch):
    """No single flush uploads more than one frame budget of texture data.

    However much DATA accumulates between draws, each flush executes at most
    ``frame_budget_bytes`` (plus at most one indivisible slab) and carries the
    rest. This applies to both 3D volumes and large 2D textures.
    """
    monkeypatch.setattr(
        'vispy.gloo.context.get_current_canvas',
        lambda: None,
    )
    parser = FakeParser()
    parser.add_texture3d(1)
    parser.add_texture2d(2)
    budget, slab = 4 * 2**20, 2**20
    try:
        assert gm.install(frame_budget_bytes=budget, slab_bytes=slab)
        state = gm._state_for(parser)
        queue = glir.GlirQueue()
        volume = np.zeros((128, 512, 512), dtype=np.uint8)  # 32 MiB
        image = np.zeros((2048, 4096), dtype=np.uint8)  # 8 MiB
        queue.command('DATA', 1, (0, 0, 0), volume)
        queue.command('DATA', 2, (0, 0), image)

        total = 0
        for _ in range(64):
            executed_before = len(parser.executed)
            state.reset_budget()  # what the per-draw canvas hook does
            queue.flush(parser)
            flushed = data_bytes(parser.executed[executed_before:])
            assert flushed <= budget + slab, (
                f'one flush uploaded {flushed} bytes '
                f'(> budget {budget} + slab {slab})'
            )
            total += flushed
            if not state.carry:
                break
        # metering bounds each frame but loses nothing overall
        assert state.carry == []
        assert total == volume.nbytes + image.nbytes
    finally:
        gm.uninstall()


class _DrainSpy:
    """Bound-method holder for add_drain_callback (WeakMethod target)."""

    def __init__(self):
        self.drains = 0

    def on_drain(self):
        self.drains += 1


def test_metered_upload_within_budget_still_notifies_drain(monkeypatch):
    """A clean flush that landed metered uploads notifies, carry or not.

    Uploads small enough to fit one frame budget are never carried, but a
    consumer may still wait for notification that their DATA commands reached
    the parser. Notification must therefore not depend on a carry queue having
    existed.
    """
    monkeypatch.setattr(
        'vispy.gloo.context.get_current_canvas',
        lambda: None,
    )
    parser = FakeParser()
    parser.add_texture3d(1)
    spy = _DrainSpy()
    try:
        assert gm.install(frame_budget_bytes=4 * 2**20, slab_bytes=2**20)
        gm.add_drain_callback(spy.on_drain)
        state = gm._state_for(parser)
        queue = glir.GlirQueue()

        # no metered uploads at all: no notification
        queue.command('UNIFORM', 7, 'u_x', 'float', 1.0)
        queue.flush(parser)
        assert spy.drains == 0

        # within-budget upload: executed immediately, never carried —
        # the flush ends clean and MUST still notify
        small = np.zeros((4, 64, 64), dtype=np.uint8)
        queue.command('DATA', 1, (0, 0, 0), small)
        queue.flush(parser)
        assert spy.drains == 1

        # over-budget upload: no notification while the carry drains,
        # exactly one when the flush that empties it ends clean
        big = np.zeros((32, 512, 512), dtype=np.uint8)  # 8 MiB
        queue.command('DATA', 1, (0, 0, 0), big)
        state.reset_budget()
        queue.flush(parser)
        assert state.carry
        assert spy.drains == 1
        for _ in range(8):
            state.reset_budget()
            queue.flush(parser)
            if not state.carry:
                break
        assert state.carry == []
        assert spy.drains == 2
    finally:
        gm.remove_drain_callback(spy.on_drain)
        gm.uninstall()


class StrictParser(FakeParser):
    """FakeParser that enforces vispy's object-existence invariant.

    Real ``GlirParser._parse`` raises ``RuntimeError(... does not
    exist)`` for object commands whose id was never created (or was
    deleted); mimic that so ordering regressions surface.
    """

    def _parse(self, command):
        cmd, id_ = command[0], command[1]
        if cmd == 'CREATE':
            self._objects[id_] = object()
        elif cmd == 'DELETE':
            self._objects.pop(id_, None)
        elif (
            cmd in ('SIZE', 'DATA', 'WRAPPING', 'INTERPOLATION')
            and id_ not in self._objects
        ):
            raise RuntimeError(
                f'Cannot {cmd} object {id_} because it does not exist',
            )
        super()._parse(command)


def test_deferred_delete_voids_later_commands(monkeypatch):
    """Commands arriving after a deferred DELETE executed must be
    dropped, not crash.

    The deferred-DELETE drain reorders deletes past later flushes, so a
    SIZE/DATA for the dead object (e.g. from another canvas's queue on
    a shared context) can reach the parser after the object is gone —
    vanilla vispy would have voided it inline. Regression test for
    ``RuntimeError: Cannot SIZE object N because it does not exist``.
    """
    monkeypatch.setattr(
        'vispy.gloo.context.get_current_canvas',
        lambda: None,
    )
    parser = StrictParser()
    try:
        assert gm.install(frame_budget_bytes=2**20, slab_bytes=2**20)
        queue = glir.GlirQueue()
        queue.command('CREATE', 5, 'VertexBuffer')
        queue.command('DELETE', 5)
        queue.flush(parser)  # quiet flush: the deferred delete drains
        state = gm._states[parser]
        assert state.deferred_deletes == []
        assert 5 in state.dead_ids
        # a late command for the dead object: dropped, no crash
        queue.command('SIZE', 5, 1024)
        queue.flush(parser)
        assert state.carry == []
        assert all(c[:2] != ('SIZE', 5) for c in parser.executed)
    finally:
        gm.uninstall()


def test_command_before_create_carried_until_create(monkeypatch):
    """A command for a not-yet-created object defers instead of crashing
    and executes once its CREATE has arrived."""
    monkeypatch.setattr(
        'vispy.gloo.context.get_current_canvas',
        lambda: None,
    )
    parser = StrictParser()
    try:
        assert gm.install(frame_budget_bytes=2**20, slab_bytes=2**20)
        queue = glir.GlirQueue()
        queue.command('SIZE', 9, 1024)
        queue.flush(parser)  # would previously raise
        state = gm._states[parser]
        assert state.carry == [('SIZE', 9, 1024)]
        queue.command('CREATE', 9, 'VertexBuffer')
        queue.flush(parser)  # carried SIZE precedes CREATE: retried
        state.reset_budget()
        queue.flush(parser)  # object now exists: the SIZE lands
        assert state.carry == []
        assert ('SIZE', 9, 1024) in parser.executed
    finally:
        gm.uninstall()
