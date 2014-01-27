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


class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)

    def _vispy_get_backend_name(self):
        return 'Glfw'

    def _vispy_process_events(self):
        self._vispy_get_native_app()  # Force exist
        pass  # not possible?
        #return glfw.glfwPollEvents(self._id)  # XXX CHECK?

    def _vispy_run(self):
        self._vispy_get_native_app()  # Force exist
        #return glfw.glfwWaitEvents(self._id)  # XXX does this work?

    def _vispy_quit(self):
        #glfw.glfwTerminate()  # XXX this can cause breakages?
        pass

    def _vispy_get_native_app(self):
        glfw.glfwInit()
        return glfw


class CanvasBackend(BaseCanvasBackend):

    """ GLUT backend for Canvas abstract class."""

    def __init__(self, name='glut window', *args, **kwargs):
        BaseCanvasBackend.__init__(self)
        self._id = glfw.glfwCreateWindow(title=name)
        glfw.glfwMakeContextCurrent(self._id)
        global ALL_WINDOWS
        ALL_WINDOWS.append(self)

        glfw.glfwHideWindow(self._id)  # Start hidden, like the other backends

        # Register callbacks
        glfw.glfwSetWindowRefreshCallback(self._id, self.on_draw)
        glfw.glfwSetWindowSizeCallback(self._id, self.on_resize)
        glfw.glfwSetKeyCallback(self._id, self.on_key_press)
        glfw.glfwSetMouseButtonCallback(self._id, self.on_mouse_action)
        glfw.glfwSetCursorPosCallback(self._id, self.on_mouse_motion)
        glfw.glfwSetWindowCloseCallback(self._id, self.on_close)
        glfw.glfwSwapInterval(1)  # avoid tearing
        # glfw.glfwFunc(self.on_)

    def _vispy_set_current(self):
        # Make this the current context
        glfw.glfwMakeContextCurrent(self._id)

    def _vispy_swap_buffers(self):
        # Swap front and back buffer
        glfw.glfwSwapBuffers(self._id)

    def _vispy_set_title(self, title):
        # Set the window title. Has no effect for widgets
        glfw.glfwSetWindowTitle(self._id, title)

    def _vispy_set_size(self, w, h):
        # Set size of the widget or window
        glfw.glfwSetWindowSize(self._id, w, h)

    def _vispy_set_position(self, x, y):
        # Set position of the widget or window. May have no effect for widgets
        glfw.glfwSetWindowPos(self._id, x, y)

    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        if visible:
            glfw.glfwShowWindow(self._id)
        else:
            glfw.glfwHideWindow(self._id)
        pass

    def _vispy_update(self):
        # Invoke a redraw
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.paint(region=None)

    def _vispy_close(self):
        # Force the window or widget to shut down
        self._vispy_set_visible(False)  # Destroying doesn't hide!
        glfw.glfwDestroyWindow(self._id)

    def _vispy_get_size(self):
        w, h = glfw.glfwGetWindowSize(self._id)
        return w, h

    def _vispy_get_position(self):
        x, y = glfw.glfwGetWindowPos(self._id)
        return x, y

    def on_show(self, _id):
        if self._vispy_canvas is None or _id != self._id:
            return
        self._vispy_canvas.events.initialize()
        # Redraw
        self._vispy_update()

    def on_resize(self, _id, w, h):
        if self._vispy_canvas is None or _id != self._id:
            return
        self._vispy_canvas.events.resize(size=(w, h))

    def on_close(self, _id):
        if self._vispy_canvas is None or _id != self._id:
            return
        self._vispy_canvas.events.close()

    def on_draw(self, _id):
        if self._vispy_canvas is None or _id != self._id:
            return
        self._vispy_canvas.events.paint(region=None)

    def on_mouse_action(self, _id, button, action, mod):
        if self._vispy_canvas is None or _id != self._id:
            return
        pos = glfw.glfwGetCursorPos()
        mod = self._process_mod(mod)
        if button < 3:
            # Mouse click event
            button = BUTTONMAP.get(button, 0)
            self._vispy_mouse_press(pos=pos, button=button,
                                    modifiers=mod)
        elif button in (3, 4):
            # Wheel event
            deltay = 1.0 if button == 3 else -1.0
            self._vispy_canvas.events.mouse_wheel(pos=pos, delta=(0.0, deltay),
                                                  modifiers=mod)

    def on_mouse_motion(self, _id, x, y):
        if self._vispy_canvas is None or _id != self._id:
            return
        self._vispy_mouse_move(pos=(x, y), modifiers=None)  # XXX

    def on_key_press(self, _id, key, scancode, action, mod):
        if self._vispy_canvas is None or _id != self._id:
            return
        key, text = self._process_key(key)
        if action == glfw.GLFW_PRESS:
            fun = self._vispy_canvas.events.key_press
        elif action == glfw.GLFW_RELEASE:
            fun = self._vispy_canvas.events.key_release
        else:
            return
        fun(key=key, text=text, modifiers=self._process_mod(mod))

    def _process_key(self, key):
        if key in KEYMAP:
            if isinstance(key, int):
                return KEYMAP[key], ''
            else:
                return KEYMAP[key], key
        elif isinstance(key, int):
            return None, ''  # unsupported special char
        else:
            return keys.Key(key.upper()), key

    def _process_mod(self, glfw_mod):
        mod = ()
        if glfw.GLFW_MOD_SHIFT & glfw_mod:
            mod += keys.SHIFT
        if glfw.GLFW_MOD_CONTRAL & glfw_mod:
            mod += keys.CONTROL
        if glfw.GLFW_MOD_ALT & glfw_mod:
            mod += keys.ALT
        return mod


class TimerBackend(BaseTimerBackend):

    def _vispy_start(self, interval):
        self._timer = None
        self.interval = interval
        self.function = self._vispy_timer._timeout
        self.is_running = False
        self._start()

    def _vispy_stop(self):
        self._timer.cancel()
        self.is_running = False

    def _run(self):
        self.is_running = False
        self._start()
        self.function()

    def _start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True
