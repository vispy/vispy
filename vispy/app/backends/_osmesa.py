# -*- coding: utf-8 -*-
# vispy: testskip
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
OSMesa backend for offscreen rendering on Linux/Unix
"""
from __future__ import division
import atexit
from time import sleep
from ...util.ptime import time
from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend)
from vispy.gloo import gl

try:
    from ...ext import osmesa
except Exception as exp:
    available, testable, why_not, which = False, False, str(exp), None
else:
    # TODO: Should be ready, no ?
    available, testable, why_not = True, True, 'Not ready for testing'
    which = 'OSMesa'

# -------------------------------------------------------------- capability ---
capability = dict(
    # if True they mean:
    title=True,          # can set title on the fly
    size=True,           # can set size on the fly
    position=False,       # can set position on the fly
    show=False,           # can show/hide window XXX ?
    vsync=False,          # can set window to sync to blank
    resizable=False,      # can toggle resizability (e.g., no user resizing)
    decorate=False,       # can toggle decorations
    fullscreen=False,     # fullscreen window support
    context=False,        # can share contexts between windows
    multi_window=False,   # can use multiple windows at once
    scroll=False,         # scroll-wheel events are supported
    parent=False,         # can pass native widget backend parent
    always_on_top=False,  # can be made always-on-top
)

# ------------------------------------------------------- set_configuration ---
def _set_config(c):
    """Set the OpenGL configuration"""
    glformat = QGLFormat()
    glformat.setRedBufferSize(c['red_size'])
    glformat.setGreenBufferSize(c['green_size'])
    glformat.setBlueBufferSize(c['blue_size'])
    glformat.setAlphaBufferSize(c['alpha_size'])
    glformat.setAccum(False)
    glformat.setRgba(True)
    glformat.setDoubleBuffer(True if c['double_buffer'] else False)
    glformat.setDepth(True if c['depth_size'] else False)
    glformat.setDepthBufferSize(c['depth_size'] if c['depth_size'] else 0)
    glformat.setStencil(True if c['stencil_size'] else False)
    glformat.setStencilBufferSize(c['stencil_size'] if c['stencil_size']
                                  else 0)
    glformat.setSampleBuffers(True if c['samples'] else False)
    glformat.setSamples(c['samples'] if c['samples'] else 0)
    glformat.setStereo(c['stereo'])
    return glformat


_VP_OSMESA_ALL_WINDOWS = []

def _get_osmesa_windows():
    return [win for win in _VP_OSMESA_ALL_WINDOWS
            if isinstance(win, CanvasBackend)]

# ------------------------------------------------------------- application ---
class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)
        self._timers = list()

    def _add_timer(self, timer):
        if timer not in self._timers:
            self._timers.append(timer)

    def _vispy_get_backend_name(self):
        return 'osmesa'

    def _vispy_process_events(self):
        for timer in self._timers:
            timer._tick()
        wins = _get_osmesa_windows()
        for win in wins:
            if win._needs_draw:
                win._needs_draw = False
                win._on_draw()

    def _vispy_run(self):
        wins = _get_osmesa_windows()
        while all(w._pixels is not None for w in wins):
            self._vispy_process_events()
        self._vispy_quit()

    def _vispy_quit(self):
        wins = _get_osmesa_windows()
        for win in wins:
            win._vispy_close()
        for timer in self._timers:
            timer._vispy_stop()
        self._timers = []

    def _vispy_get_native_app(self):
        return osmesa

# ------------------------------------------------------------------ canvas ---

class CanvasBackend(BaseCanvasBackend):
    """OSMesa backend for Canvas"""

    # args are for BaseCanvasBackend, kwargs are for us.
    def __init__(self, *args, **kwargs):
        BaseCanvasBackend.__init__(self, *args)
        # We use _process_backend_kwargs() to "serialize" the kwargs
        # and to check whether they match this backend's capability
        p = self._process_backend_kwargs(kwargs)

        # Deal with config
        # ... use context.config
        # Deal with context
        p.context.shared.add_ref('osmesa', self)
        if p.context.shared.ref is self:
            self._native_context = osmesa.OSMesaCreateContext()
        else:
            self._native_context = p.context.shared.ref._native_context

        self._pixels = None
        self._vispy_set_size(*p.size)
        _VP_OSMESA_ALL_WINDOWS.append(self)

        self._vispy_canvas.set_current()
        self._vispy_canvas.events.initialize()

    def _vispy_set_current(self):
        if self._pixels is None:
            return
        ok = osmesa.OSMesaMakeCurrent(self._native_context, self._pixels,
                                      self._size[0], self._size[1])
        if not ok:
            raise RuntimeError('Failed attaching OSMesa rendering buffer')

    def _vispy_swap_buffers(self):
        if self._pixels is None:
            return
        gl.glFinish()

    def _vispy_set_title(self, title):
        pass

    def _vispy_set_size(self, w, h):
        self._pixels = osmesa.allocate_pixels_buffer(w, h)
        self._size = (w, h)
        self._vispy_set_current()
        self._vispy_update()

    def _vispy_set_position(self, x, y):
        pass

    def _vispy_set_visible(self, visible):
        pass

    def _vispy_set_fullscreen(self, fullscreen):
        pass

    def _vispy_update(self):
        # This is checked by osmesa ApplicationBackend in process_events
        self._needs_draw = True

    def _vispy_close(self):
        osmesa.OSMesaDestroyContext(self._native_context)
        self._native_context = None
        self._pixels = None

    def _vispy_get_size(self):
        if self._pixels is None:
            return
        return self._size

    def _vispy_get_position(self):
        return 0, 0

    def _vispy_get_fullscreen(self):
        return False

    def _on_draw(self):
        # This is called by the osmesa ApplicationBackend
        if self._vispy_canvas is None or self._pixels is None:
            return
        self._vispy_canvas.set_current()
        self._vispy_canvas.events.draw(region=None) # (0, 0, w, h)

# ------------------------------------------------------------------- timer ---

class TimerBackend(BaseTimerBackend):

    def __init__(self, vispy_timer):
        BaseTimerBackend.__init__(self, vispy_timer)
        vispy_timer._app._backend._add_timer(self)
        self._vispy_stop()

    def _vispy_start(self, interval):
        self._interval = interval
        self._next_time = time() + self._interval

    def _vispy_stop(self):
        self._next_time = float('inf')

    def _tick(self):
        if time() > self._next_time:
            self._vispy_timer._timeout()
            self._next_time = time() + self._interval

