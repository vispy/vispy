# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
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

from threading import Timer

from ..base import BaseApplicationBackend, BaseCanvasBackend, BaseTimerBackend
from ...util import keys

from . import _libglfw as glfw


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


ALL_WINDOWS = []


MOD_KEYS = [keys.SHIFT, keys.ALT, keys.CONTROL, keys.META]


def _get_glfw_windows(check=False):
    wins = list()
    global ALL_WINDOWS
    for win in ALL_WINDOWS:
        if isinstance(win, CanvasBackend):
            wins.append(win)
    if check and len(wins) != 1:
        raise RuntimeError('Can only use a single window')
    return wins


_do_draw = False


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
        wins = _get_glfw_windows()
        for win in wins:
            glfw.glfwPollEvents(win._id)

    def _vispy_run(self):
        win = _get_glfw_windows(check=True)[0]
        global _do_draw
        while win._id is not None and not glfw.glfwWindowShouldClose(win._id):
            if _do_draw:
                win._on_draw()
            glfw.glfwPollEvents()
        self._vispy_quit()

    def _vispy_quit(self):
        wins = _get_glfw_windows()
        for win in wins:
            win._vispy_close()
        # tear down timers
        for timer in self._timers:
            timer._vispy_stop()
        self._timers = []

    def _vispy_get_native_app(self):
        return glfw


class CanvasBackend(BaseCanvasBackend):

    """ GLUT backend for Canvas abstract class."""

    def __init__(self, name='glut window', *args, **kwargs):
        BaseCanvasBackend.__init__(self)
        # Init GLFW, add window hints, and create window
        glfw.glfwInit()
        glfw.glfwWindowHint(glfw.GLFW_REFRESH_RATE, 0)
        glfw.glfwWindowHint(glfw.GLFW_RESIZABLE, True)
        glfw.glfwWindowHint(glfw.GLFW_DEPTH_BITS, 24)
        glfw.glfwWindowHint(glfw.GLFW_RED_BITS, 8)
        glfw.glfwWindowHint(glfw.GLFW_GREEN_BITS, 8)
        glfw.glfwWindowHint(glfw.GLFW_BLUE_BITS, 8)
        glfw.glfwWindowHint(glfw.GLFW_ALPHA_BITS, 8)
        glfw.glfwWindowHint(glfw.GLFW_RESIZABLE, True)
        glfw.glfwWindowHint(glfw.GLFW_DECORATED, True)
        glfw.glfwWindowHint(glfw.GLFW_VISIBLE, True)
        self._id = glfw.glfwCreateWindow(title=name)
        glfw.glfwMakeContextCurrent(self._id)
        glfw.glfwHideWindow(self._id)  # Start hidden, like the other backends
        global ALL_WINDOWS
        ALL_WINDOWS.append(self)
        self._mod = list()

        # Register callbacks
        glfw.glfwSetWindowRefreshCallback(self._id, self._on_draw)
        glfw.glfwSetFramebufferSizeCallback(self._id, self._on_resize)
        glfw.glfwSetKeyCallback(self._id, self._on_key_press)
        glfw.glfwSetMouseButtonCallback(self._id, self._on_mouse_button)
        glfw.glfwSetScrollCallback(self._id, self._on_mouse_scroll)
        glfw.glfwSetCursorPosCallback(self._id, self._on_mouse_motion)
        glfw.glfwSetWindowCloseCallback(self._id, self._on_close)
        glfw.glfwSwapInterval(1)  # avoid tearing
        self._vispy_canvas_ = None

    ###########################################################################
    # Deal with events we get from vispy
    @property
    def _vispy_canvas(self):
        """ The size of canvas/window """
        return self._vispy_canvas_

    @_vispy_canvas.setter
    def _vispy_canvas(self, vc):
        # Init events when the property is set by Canvas
        self._vispy_canvas_ = vc
        if vc is not None:
            self._vispy_canvas.events.initialize()
        return self._vispy_canvas

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
        else:
            glfw.glfwHideWindow(self._id)

    def _vispy_update(self):
        # Invoke a redraw, passing it on to the canvas
        if self._vispy_canvas is None or self._id is None:
            return
        # XXX HACKISH SOLUTION
        global _do_draw
        _do_draw = True
        #self._on_draw(self._id)

    def _vispy_close(self):
        # Force the window or widget to shut down
        self._vispy_set_visible(False)  # Destroying doesn't hide!
        global ALL_WINDOWS
        if self in ALL_WINDOWS and self._id is not None:
            ALL_WINDOWS.pop(ALL_WINDOWS.index(self))
            glfw.glfwDestroyWindow(self._id)
            self._id = None

    def _vispy_get_size(self):
        if self._id is None:
            return
        w, h = glfw.glfwGetFramebufferSize(self._id)
        return w, h

    def _vispy_get_position(self):
        if self._id is None:
            return
        x, y = glfw.glfwGetWindowPos(self._id)
        return x, y

    ###########################################################################
    # Notify vispy of events triggered by GLFW
    def _on_resize(self, _id, w, h):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.resize(size=(w, h))

    def _on_close(self, _id):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.close()

    def _on_draw(self, _id=None):
        if self._vispy_canvas is None or self._id is None:
            return
        self._vispy_canvas.events.paint(region=None)  # (0, 0, w, h))

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
        fun(key=key, text=text, modifiers=self._mod)

    def _process_key(self, key):
        if key in KEYMAP:
            return KEYMAP[key], ''
        elif 32 <= key <= 127:
            return keys.Key(chr(key)), chr(key)
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


class TimerBackend(BaseTimerBackend):

    def __init__(self, vispy_timer):
        BaseTimerBackend.__init__(self, vispy_timer)
        # tell application instance about existence
        vispy_timer._app._backend._add_timer(self)

    def _vispy_start(self, interval):
        self._timer = None
        self.interval = interval
        self.is_running = False
        self._start()

    def _vispy_stop(self):
        self._timer.cancel()
        self.is_running = False

    def _run(self):
        self.is_running = False
        self._start()
        self._vispy_timer._timeout()

    def _start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True
