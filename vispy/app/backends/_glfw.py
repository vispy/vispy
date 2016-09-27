# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
vispy backend for glfw.
"""

# Note: to install GLFW on Ubuntu:
# $ git clone git://github.com/glfw/glfw.git
# $ cd glfw
# $ cmake -DBUILD_SHARED_LIBS=true -DGLFW_BUILD_EXAMPLES=false \
#         -DGLFW_BUILD_TESTS=false -DGLFW_BUILD_DOCS=false .
# $ make
# $ sudo make install
# $ sudo apt-get -qq install libx11-dev

# On OSX, consider using brew.

from __future__ import division

import atexit
from time import sleep
import gc
import os

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend)
from ...util import keys, logger
from ...util.ptime import time
from ... import config

USE_EGL = config['gl_backend'].lower().startswith('es')


# -------------------------------------------------------------------- init ---

try:
    from ...ext import glfw

    # Map native keys to vispy keys
    KEYMAP = {
        glfw.GLFW_KEY_LEFT_SHIFT: keys.SHIFT,
        glfw.GLFW_KEY_RIGHT_SHIFT: keys.SHIFT,
        glfw.GLFW_KEY_LEFT_CONTROL: keys.CONTROL,
        glfw.GLFW_KEY_RIGHT_CONTROL: keys.CONTROL,
        glfw.GLFW_KEY_LEFT_ALT: keys.ALT,
        glfw.GLFW_KEY_RIGHT_ALT: keys.ALT,
        glfw.GLFW_KEY_LEFT_SUPER: keys.META,
        glfw.GLFW_KEY_RIGHT_SUPER: keys.META,

        glfw.GLFW_KEY_LEFT: keys.LEFT,
        glfw.GLFW_KEY_UP: keys.UP,
        glfw.GLFW_KEY_RIGHT: keys.RIGHT,
        glfw.GLFW_KEY_DOWN: keys.DOWN,
        glfw.GLFW_KEY_PAGE_UP: keys.PAGEUP,
        glfw.GLFW_KEY_PAGE_DOWN: keys.PAGEDOWN,

        glfw.GLFW_KEY_INSERT: keys.INSERT,
        glfw.GLFW_KEY_DELETE: keys.DELETE,
        glfw.GLFW_KEY_HOME: keys.HOME,
        glfw.GLFW_KEY_END: keys.END,

        glfw.GLFW_KEY_ESCAPE: keys.ESCAPE,
        glfw.GLFW_KEY_BACKSPACE: keys.BACKSPACE,

        glfw.GLFW_KEY_F1: keys.F1,
        glfw.GLFW_KEY_F2: keys.F2,
        glfw.GLFW_KEY_F3: keys.F3,
        glfw.GLFW_KEY_F4: keys.F4,
        glfw.GLFW_KEY_F5: keys.F5,
        glfw.GLFW_KEY_F6: keys.F6,
        glfw.GLFW_KEY_F7: keys.F7,
        glfw.GLFW_KEY_F8: keys.F8,
        glfw.GLFW_KEY_F9: keys.F9,
        glfw.GLFW_KEY_F10: keys.F10,
        glfw.GLFW_KEY_F11: keys.F11,
        glfw.GLFW_KEY_F12: keys.F12,

        glfw.GLFW_KEY_SPACE: keys.SPACE,
        glfw.GLFW_KEY_ENTER: keys.ENTER,
        '\r': keys.ENTER,
        glfw.GLFW_KEY_TAB: keys.TAB,
    }

    BUTTONMAP = {glfw.GLFW_MOUSE_BUTTON_LEFT: 1,
                 glfw.GLFW_MOUSE_BUTTON_RIGHT: 2,
                 glfw.GLFW_MOUSE_BUTTON_MIDDLE: 3
                 }
except Exception as exp:
    available, testable, why_not, which = False, False, str(exp), None
else:
    if USE_EGL:
        available, testable, why_not = False, False, 'EGL not supported'
        which = 'glfw ' + str(glfw.__version__)
    else:
        available, testable, why_not = True, True, None
        which = 'glfw ' + str(glfw.__version__)

MOD_KEYS = [keys.SHIFT, keys.ALT, keys.CONTROL, keys.META]
_GLFW_INITIALIZED = False
_VP_GLFW_ALL_WINDOWS = []


def _get_glfw_windows():
    wins = list()
    for win in _VP_GLFW_ALL_WINDOWS:
        if isinstance(win, CanvasBackend):
            wins.append(win)
    return wins


# -------------------------------------------------------------- capability ---

capability = dict(  # things that can be set by the backend
    title=True,
    size=True,
    position=True,
    show=True,
    vsync=True,
    resizable=True,
    decorate=True,
    fullscreen=True,
    context=True,
    multi_window=True,
    scroll=True,
    parent=False,
    always_on_top=True,
)


# ------------------------------------------------------- set_configuration ---

def _set_config(c):
    """Set gl configuration for GLFW """
    glfw.glfwWindowHint(glfw.GLFW_RED_BITS, c['red_size'])
    glfw.glfwWindowHint(glfw.GLFW_GREEN_BITS, c['green_size'])
    glfw.glfwWindowHint(glfw.GLFW_BLUE_BITS, c['blue_size'])
    glfw.glfwWindowHint(glfw.GLFW_ALPHA_BITS, c['alpha_size'])

    glfw.glfwWindowHint(glfw.GLFW_ACCUM_RED_BITS, 0)
    glfw.glfwWindowHint(glfw.GLFW_ACCUM_GREEN_BITS, 0)
    glfw.glfwWindowHint(glfw.GLFW_ACCUM_BLUE_BITS, 0)
    glfw.glfwWindowHint(glfw.GLFW_ACCUM_ALPHA_BITS, 0)

    glfw.glfwWindowHint(glfw.GLFW_DEPTH_BITS, c['depth_size'])
    glfw.glfwWindowHint(glfw.GLFW_STENCIL_BITS, c['stencil_size'])
    # glfw.glfwWindowHint(glfw.GLFW_CONTEXT_VERSION_MAJOR, c['major_version'])
    # glfw.glfwWindowHint(glfw.GLFW_CONTEXT_VERSION_MINOR, c['minor_version'])
    # glfw.glfwWindowHint(glfw.GLFW_SRGB_CAPABLE, c['srgb'])
    glfw.glfwWindowHint(glfw.GLFW_SAMPLES, c['samples'])
    glfw.glfwWindowHint(glfw.GLFW_STEREO, c['stereo'])
    if not c['double_buffer']:
        raise RuntimeError('GLFW must double buffer, consider using a '
                           'different backend, or using double buffering')


# ------------------------------------------------------------- application ---


_glfw_errors = []


def _error_callback(num, descr):
    _glfw_errors.append('Error %s: %s' % (num, descr))


class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)
        self._timers = list()

    def _add_timer(self, timer):
        if timer not in self._timers:
            self._timers.append(timer)

    def _vispy_get_backend_name(self):
        return 'Glfw'

    def _vispy_process_events(self):
        glfw.glfwPollEvents()
        for timer in self._timers:
            timer._tick()
        wins = _get_glfw_windows()
        for win in wins:
            if win._needs_draw:
                win._needs_draw = False
                win._on_draw()

    def _vispy_run(self):
        wins = _get_glfw_windows()
        while any(w._id is not None and not glfw.glfwWindowShouldClose(w._id)
                  for w in wins):
            self._vispy_process_events()
        self._vispy_quit()  # to clean up

    def _vispy_quit(self):
        # Close windows
        wins = _get_glfw_windows()
        for win in wins:
            if win._vispy_canvas is not None:
                win._vispy_canvas.close()
        # tear down timers
        for timer in self._timers:
            timer._vispy_stop()
        self._timers = []

    def _vispy_get_native_app(self):
        global _GLFW_INITIALIZED
        if not _GLFW_INITIALIZED:
            cwd = os.getcwd()
            glfw.glfwSetErrorCallback(_error_callback)
            try:
                if not glfw.glfwInit():  # only ever call once
                    raise OSError('Could not init glfw:\n%r' % _glfw_errors)
            finally:
                os.chdir(cwd)
            glfw.glfwSetErrorCallback(0)
            atexit.register(glfw.glfwTerminate)
            _GLFW_INITIALIZED = True
        return glfw


# ------------------------------------------------------------------ canvas ---

class CanvasBackend(BaseCanvasBackend):

    """ Glfw backend for Canvas abstract class."""

    # args are for BaseCanvasBackend, kwargs are for us.
    def __init__(self, *args, **kwargs):
        BaseCanvasBackend.__init__(self, *args)
        p = self._process_backend_kwargs(kwargs)
        self._initialized = False

        # Deal with config
        _set_config(p.context.config)
        # Deal with context
        p.context.shared.add_ref('glfw', self)
        if p.context.shared.ref is self:
            share = None
        else:
            share = p.context.shared.ref._id

        glfw.glfwWindowHint(glfw.GLFW_REFRESH_RATE, 0)  # highest possible
        glfw.glfwSwapInterval(1 if p.vsync else 0)
        glfw.glfwWindowHint(glfw.GLFW_RESIZABLE, int(p.resizable))
        glfw.glfwWindowHint(glfw.GLFW_DECORATED, int(p.decorate))
        glfw.glfwWindowHint(glfw.GLFW_VISIBLE, 0)  # start out hidden
        glfw.glfwWindowHint(glfw.GLFW_FLOATING, int(p.always_on_top))
        if p.fullscreen is not False:
            self._fullscreen = True
            if p.fullscreen is True:
                monitor = glfw.glfwGetPrimaryMonitor()
            else:
                monitor = glfw.glfwGetMonitors()
                if p.fullscreen >= len(monitor):
                    raise ValueError('fullscreen must be <= %s'
                                     % len(monitor))
                monitor = monitor[p.fullscreen]
            use_size = glfw.glfwGetVideoMode(monitor)[:2]
            if use_size != tuple(p.size):
                logger.debug('Requested size %s, will be ignored to '
                             'use fullscreen mode %s' % (p.size, use_size))
            size = use_size
        else:
            self._fullscreen = False
            monitor = None
            size = p.size

        self._id = glfw.glfwCreateWindow(width=size[0], height=size[1],
                                         title=p.title, monitor=monitor,
                                         share=share)
        if not self._id:
            raise RuntimeError('Could not create window')

        _VP_GLFW_ALL_WINDOWS.append(self)
        self._mod = list()

        # Register callbacks
        glfw.glfwSetWindowRefreshCallback(self._id, self._on_draw)
        glfw.glfwSetWindowSizeCallback(self._id, self._on_resize)
        glfw.glfwSetKeyCallback(self._id, self._on_key_press)
        glfw.glfwSetCharCallback(self._id, self._on_key_char)
        glfw.glfwSetMouseButtonCallback(self._id, self._on_mouse_button)
        glfw.glfwSetScrollCallback(self._id, self._on_mouse_scroll)
        glfw.glfwSetCursorPosCallback(self._id, self._on_mouse_motion)
        glfw.glfwSetWindowCloseCallback(self._id, self._on_close)
        self._vispy_canvas_ = None
        self._needs_draw = False
        self._vispy_canvas.set_current()
        if p.position is not None:
            self._vispy_set_position(*p.position)
        if p.show:
            glfw.glfwShowWindow(self._id)

        # Init
        self._initialized = True
        self._next_key_events = []
        self._next_key_text = {}
        self._vispy_canvas.set_current()
        self._vispy_canvas.events.initialize()

    def _vispy_warmup(self):
        etime = time() + 0.25
        while time() < etime:
            sleep(0.01)
            self._vispy_canvas.set_current()
            self._vispy_canvas.app.process_events()

    def _vispy_set_current(self):
        if self._id is None:
            return
        # Make this the current context
        glfw.glfwMakeContextCurrent(self._id)

    def _vispy_swap_buffers(self):
        if self._id is None:
            return
        # Swap front and back buffer
        glfw.glfwSwapBuffers(self._id)

    def _vispy_set_title(self, title):
        if self._id is None:
            return
        # Set the window title. Has no effect for widgets
        glfw.glfwSetWindowTitle(self._id, title)

    def _vispy_set_size(self, w, h):
        if self._id is None:
            return
        # Set size of the widget or window
        glfw.glfwSetWindowSize(self._id, w, h)

    def _vispy_set_position(self, x, y):
        if self._id is None:
            return
        # Set position of the widget or window. May have no effect for widgets
        glfw.glfwSetWindowPos(self._id, x, y)

    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        if self._id is None:
            return
        if visible:
            glfw.glfwShowWindow(self._id)
            # this ensures that the show takes effect
            self._vispy_update()
        else:
            glfw.glfwHideWindow(self._id)

    def _vispy_set_fullscreen(self, fullscreen):
        logger.warn('Cannot change fullscreen mode for GLFW backend')

    def _vispy_update(self):
        # Invoke a redraw, passing it on to the canvas
        if self._vispy_canvas is None or self._id is None:
            return
        # Mark that this window wants to be drawn on the next loop iter
        self._needs_draw = True

    def _vispy_close(self):
        # Force the window or widget to shut down
        if self._id is not None:
            self._vispy_canvas = None
            # glfw.glfwSetWindowShouldClose()  # Does not really cause a close
            self._vispy_set_visible(False)
            self._id, id_ = None, self._id
            glfw.glfwDestroyWindow(id_)
            gc.collect()  # help ensure context gets destroyed

    def _vispy_get_size(self):
        if self._id is None:
            return
        w, h = glfw.glfwGetWindowSize(self._id)
        return w, h

    def _vispy_get_physical_size(self):
        if self._id is None:
            return
        w, h = glfw.glfwGetFramebufferSize(self._id)
        return w, h

    def _vispy_get_position(self):
        if self._id is None:
            return
        x, y = glfw.glfwGetWindowPos(self._id)
        return x, y

    def _vispy_get_fullscreen(self):
        return self._fullscreen

    ##########################################
    # Notify vispy of events triggered by GLFW
    def _on_resize(self, _id, w, h):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.resize(
            size=(w, h), physical_size=self._vispy_get_physical_size())

    def _on_close(self, _id):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.close()

    def _on_draw(self, _id=None):
        if self._vispy_canvas is None or self._id is None:
            return
        self._vispy_canvas.set_current()
        self._vispy_canvas.events.draw(region=None)  # (0, 0, w, h))

    def _on_mouse_button(self, _id, button, action, mod):
        if self._vispy_canvas is None and self._id is not None:
            return
        pos = glfw.glfwGetCursorPos(self._id)
        if button < 3:
            # Mouse click event
            button = BUTTONMAP.get(button, 0)
            if action == glfw.GLFW_PRESS:
                fun = self._vispy_mouse_press
            elif action == glfw.GLFW_RELEASE:
                fun = self._vispy_mouse_release
            else:
                return
            fun(pos=pos, button=button, modifiers=self._mod)

    def _on_mouse_scroll(self, _id, x_off, y_off):
        if self._vispy_canvas is None and self._id is not None:
            return
        pos = glfw.glfwGetCursorPos(self._id)
        delta = (float(x_off), float(y_off))
        self._vispy_canvas.events.mouse_wheel(pos=pos, delta=delta,
                                              modifiers=self._mod)

    def _on_mouse_motion(self, _id, x, y):
        if self._vispy_canvas is None:
            return
        self._vispy_mouse_move(pos=(x, y), modifiers=self._mod)

    def _on_key_press(self, _id, key, scancode, action, mod):
        if self._vispy_canvas is None:
            return
        key, text = self._process_key(key)
        if action == glfw.GLFW_PRESS:
            fun = self._vispy_canvas.events.key_press
            down = True
        elif action == glfw.GLFW_RELEASE:
            fun = self._vispy_canvas.events.key_release
            down = False
        else:
            return
        self._process_mod(key, down=down)
        
        # NOTE: GLFW only provides localized characters via _on_key_char, so if
        # this event contains a character we store all other data and dispatch
        # it once the final unicode character is sent shortly after.
        if text != '' and action == glfw.GLFW_PRESS:
            self._next_key_events.append((fun, key, self._mod))
        else:
            if key in self._next_key_text:
                text = self._next_key_text[key]
                del self._next_key_text[key]
            fun(key=key, text=text, modifiers=self._mod)

    def _on_key_char(self, _id, text):
        # Repeat strokes (frequency configured at OS) are sent here only,
        # no regular _on_key_press events. Currently ignored!
        if len(self._next_key_events) == 0:
            return

        (fun, key, mod) = self._next_key_events.pop(0)
        fun(key=key, text=chr(text), modifiers=mod)
        self._next_key_text[key] = text

    def _process_key(self, key):
        if 32 <= key <= 127:
            return keys.Key(chr(key)), chr(key)
        elif key in KEYMAP:
            return KEYMAP[key], ''
        else:
            return None, ''

    def _process_mod(self, key, down):
        """Process (possible) keyboard modifiers

        GLFW provides "mod" with many callbacks, but not (critically) the
        scroll callback, so we keep track on our own here.
        """
        if key in MOD_KEYS:
            if down:
                if key not in self._mod:
                    self._mod.append(key)
            elif key in self._mod:
                self._mod.pop(self._mod.index(key))
        return self._mod


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
