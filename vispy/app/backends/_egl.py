# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
vispy headless backend for egl.
"""

from __future__ import division

import atexit
from time import sleep

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend)
from ...util.ptime import time

# -------------------------------------------------------------------- init ---

try:
    # Inspired by http://www.mesa3d.org/egl.html
    # This is likely necessary on Linux since proprietary drivers
    # (e.g., NVIDIA) are unlikely to provide EGL support for now.
    # XXX TODO: Add use_gl('es2') and somehow incorporate here.
    # Also would be good to have us_gl('es3'), since libGLESv2.so on linux
    # seems to support both.
    from os import environ
    environ['EGL_SOFTWARE'] = 'true'
    from ...ext import egl
    _EGL_DISPLAY = egl.eglGetDisplay()
    egl.eglInitialize(_EGL_DISPLAY)
    version = [egl.eglQueryString(_EGL_DISPLAY, x) for x in
               [egl.EGL_VERSION, egl.EGL_VENDOR, egl.EGL_CLIENT_APIS]]
    version = [v.decode('utf-8') for v in version]
    version = version[0] + ' ' + version[1] + ': ' + version[2].strip()
    atexit.register(egl.eglTerminate, _EGL_DISPLAY)
except Exception as exp:
    available, testable, why_not, which = False, False, str(exp), None
else:
    # XXX restore "testable" and "available" once it works properly, and
    # remove from ignore list in .coveragerc
    available, testable, why_not = False, False, 'Not ready for testing'
    which = 'EGL ' + str(version)


_VP_EGL_ALL_WINDOWS = []


def _get_egl_windows():
    wins = list()
    for win in _VP_EGL_ALL_WINDOWS:
        if isinstance(win, CanvasBackend):
            wins.append(win)
    return wins


# -------------------------------------------------------------- capability ---

capability = dict(  # things that can be set by the backend
    title=True,
    size=True,
    position=True,
    show=True,
    vsync=False,
    resizable=True,
    decorate=False,
    fullscreen=False,
    context=False,
    multi_window=True,
    scroll=False,
    parent=False,
    always_on_top=False,
)


# ------------------------------------------------------------- application ---

class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)
        self._timers = list()

    def _add_timer(self, timer):
        if timer not in self._timers:
            self._timers.append(timer)

    def _vispy_get_backend_name(self):
        return 'egl'

    def _vispy_process_events(self):
        for timer in self._timers:
            timer._tick()
        wins = _get_egl_windows()
        for win in wins:
            if win._needs_draw:
                win._needs_draw = False
                win._on_draw()

    def _vispy_run(self):
        wins = _get_egl_windows()
        while all(w._surface is not None for w in wins):
            self._vispy_process_events()
        self._vispy_quit()  # to clean up

    def _vispy_quit(self):
        # Close windows
        wins = _get_egl_windows()
        for win in wins:
            win._vispy_close()
        # tear down timers
        for timer in self._timers:
            timer._vispy_stop()
        self._timers = []

    def _vispy_get_native_app(self):
        return egl


# ------------------------------------------------------------------ canvas ---

class CanvasBackend(BaseCanvasBackend):

    """ EGL backend for Canvas abstract class."""

    # args are for BaseCanvasBackend, kwargs are for us.
    def __init__(self, *args, **kwargs):
        BaseCanvasBackend.__init__(self, *args)
        p = self._process_backend_kwargs(kwargs)
        self._initialized = False

        # Deal with context
        p.context.shared.add_ref('egl', self)
        if p.context.shared.ref is self:
            # Store context information
            self._native_config = egl.eglChooseConfig(_EGL_DISPLAY)[0]
            self._native_context = egl.eglCreateContext(_EGL_DISPLAY,
                                                        self._native_config,
                                                        None)
        else:
            # Reuse information from other context
            self._native_config = p.context.shared.ref._native_config
            self._native_context = p.context.shared.ref._native_context

        self._surface = None
        self._vispy_set_size(*p.size)
        _VP_EGL_ALL_WINDOWS.append(self)

        # Init
        self._initialized = True
        self._vispy_canvas.set_current()
        self._vispy_canvas.events.initialize()

    def _destroy_surface(self):
        if self._surface is not None:
            egl.eglDestroySurface(_EGL_DISPLAY, self._surface)
            self._surface = None

    def _vispy_set_size(self, w, h):
        if self._surface is not None:
            self._destroy_surface()
        attrib_list = (egl.EGL_WIDTH, w, egl.EGL_HEIGHT, h)
        self._surface = egl.eglCreatePbufferSurface(_EGL_DISPLAY,
                                                    self._native_config,
                                                    attrib_list)
        if self._surface == egl.EGL_NO_SURFACE:
            raise RuntimeError('Could not create rendering surface')
        self._size = (w, h)
        self._vispy_update()

    def _vispy_warmup(self):
        etime = time() + 0.25
        while time() < etime:
            sleep(0.01)
            self._vispy_canvas.set_current()
            self._vispy_canvas.app.process_events()

    def _vispy_set_current(self):
        if self._surface is None:
            return
        # Make this the current context
        self._vispy_canvas.set_current()  # Mark canvs as current
        egl.eglMakeCurrent(_EGL_DISPLAY, self._surface, self._surface,
                           self._native_context)

    def _vispy_swap_buffers(self):
        if self._surface is None:
            return
        # Swap front and back buffer
        egl.eglSwapBuffers(_EGL_DISPLAY, self._surface)

    def _vispy_set_title(self, title):
        pass

    def _vispy_set_position(self, x, y):
        pass

    def _vispy_set_visible(self, visible):
        pass

    def _vispy_update(self):
        # Mark that this window wants to be drawn on the next loop iter
        self._needs_draw = True

    def _vispy_close(self):
        self._destroy_surface()

    def _vispy_get_size(self):
        if self._surface is None:
            return
        return self._size

    def _vispy_get_position(self):
        return 0, 0

    def _on_draw(self, _id=None):
        # This is called by the processing app
        if self._vispy_canvas is None or self._surface is None:
            return
        self._vispy_canvas.set_current()
        self._vispy_canvas.events.draw(region=None)  # (0, 0, w, h))


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
        if time() >= self._next_time:
            self._vispy_timer._timeout()
            self._next_time = time() + self._interval
