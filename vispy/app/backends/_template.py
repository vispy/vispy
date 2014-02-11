# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" This module provides an template for creating backends for vispy.
It clearly indicates what methods should be implemented and what events
should be emitted.
"""

from __future__ import division

from ... import app
from ...util import keys

# Map native keys to vispy keys
KEYMAP = {
    -1: keys.SHIFT,
    -2: keys.CONTROL,
    -3: keys.ALT,
    -4: keys.META,

    -5: keys.LEFT,
    -6: keys.UP,
    -7: keys.RIGHT,
    -8: keys.DOWN,
    -9: keys.PAGEUP,
    -10: keys.PAGEDOWN,

    -11: keys.INSERT,
    -12: keys.DELETE,
    -13: keys.HOME,
    -14: keys.END,

    -15: keys.ESCAPE,
    -16: keys.BACKSPACE,

    -17: keys.SPACE,
    -18: keys.ENTER,
    -19: keys.TAB,

    -20: keys.F1,
    -21: keys.F2,
    -22: keys.F3,
    -23: keys.F4,
    -24: keys.F5,
    -25: keys.F6,
    -26: keys.F7,
    -27: keys.F8,
    -28: keys.F9,
    -29: keys.F10,
    -30: keys.F11,
    -31: keys.F12,
}


class ApplicationBackend(app.ApplicationBackend):

    def __init__(self):
        app.ApplicationBackend.__init__(self)

    def _vispy_get_backend_name(self):
        return 'ThisBackendsName'

    def _vispy_process_events(self):
        raise NotImplementedError()

    def _vispy_run(self):
        raise NotImplementedError()

    def _vispy_quit(self):
        raise NotImplementedError()

    def _vispy_get_native_app(self):
        raise NotImplementedError()


# You can mix this class with the native widget
class CanvasBackend(app.CanvasBackend):

    def __init__(self, vispy_canvas, *args, **kwargs):
        #NativeWidgetClass.__init__(self, *args, **kwargs)
        app.CanvasBackend.__init__(self, vispy_canvas)

    def _vispy_set_current(self):
        # Make this the current context
        raise NotImplementedError()

    def _vispy_swap_buffers(self):
        # Swap front and back buffer
        raise NotImplementedError()

    def _vispy_set_title(self, title):
        # Set the window title. Has no effect for widgets
        raise NotImplementedError()

    def _vispy_set_size(self, w, h):
        # Set size of the widget or window
        raise NotImplementedError()

    def _vispy_set_position(self, x, y):
        # Set location of the widget or window. May have no effect for widgets
        raise NotImplementedError()

    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        raise NotImplementedError()

    def _vispy_update(self):
        # Invoke a redraw
        raise NotImplementedError()

    def _vispy_close(self):
        # Force the window or widget to shut down
        raise NotImplementedError()

    def _vispy_get_size(self):
        # Should return widget size
        raise NotImplementedError()

    def _vispy_get_position(self):
        # Should return widget position
        raise NotImplementedError()

    def _vispy_get_native_canvas(self):
        # Should return the native widget object.
        # If this is self, this method can be omitted.
        return self

    def events_to_emit(self):
        """ Shown here in one method, but most backends will probably
        have one method for each event.
        """
        raise NotImplementedError
        """
        if self._vispy_canvas is None:
            return

        self._vispy_canvas.events.initialize()
        self._vispy_canvas.events.resize(size=(w, h))
        self._vispy_canvas.events.paint(region=None)
        self._vispy_canvas.events.close()

        self._vispy_canvas.events.mouse_press(
            pos=(
                x,
                y),
            button=1,
            modifiers=())
        self._vispy_canvas.events.mouse_release(
            pos=(
                x,
                y),
            button=1,
            modifiers=())
        self._vispy_canvas.events.mouse_move(pos=(x, y), modifiers=())
        self._vispy_canvas.events.mouse_wheel(
            pos=(
                x, y), delta=(
                0, 0), modifiers=())

        self._vispy_canvas.events.key_press(key=key, text=text, modifiers=())
        self._vispy_canvas.events.key_release(key=key, text=text, modifiers=())
        """


class TimerBackend(app.TimerBackend):  # Can be mixed with native timer class

    def __init__(self, vispy_timer):
        app.TimerBackend.__init__(self, vispy_timer)

    def _vispy_start(self, interval):
        raise NotImplementedError()

    def _vispy_stop(self):
        raise NotImplementedError()

    def _vispy_timeout(self):
        raise NotImplementedError()

    def _vispy_get_native_timer(self):
        # Should return the native widget object.
        # If this is self, this method can be omitted.
        return self
