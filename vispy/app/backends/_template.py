# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" This module provides an template for creating backends for vispy.
It clearly indicates what methods should be implemented and what events
should be emitted.
"""

from __future__ import division

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend)
from ...util import keys
from ... import config

USE_EGL = config['gl_backend'].lower().startswith('es')


# -------------------------------------------------------------------- init ---

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


# -------------------------------------------------------------- capability ---

# These are all booleans. Note that they mirror many of the kwargs to
# the initialization of the Canvas class.
capability = dict(
    # if True they mean:
    title=False,          # can set title on the fly
    size=False,           # can set size on the fly
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
    """Set gl configuration for template"""
    raise NotImplementedError


# ------------------------------------------------------------- application ---

class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)

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


# ------------------------------------------------------------------ canvas ---

# You can mix this class with the native widget
class CanvasBackend(BaseCanvasBackend):
    """Template backend

    Events to emit are shown below. Most backends will probably
    have one method for each event:

        self._vispy_canvas.events.initialize()
        self._vispy_canvas.events.resize(size=(w, h))
        self._vispy_canvas.events.draw(region=None)
        self._vispy_canvas.close()
        self._vispy_canvas.events.mouse_press(pos=(x, y), button=1,
                                              modifiers=())
        self._vispy_canvas.events.mouse_release(pos=(x, y), button=1,
                                                modifiers=())
        self._vispy_canvas.events.mouse_double_click(pos=(x, y), button=1,
                                                     modifiers=())
        self._vispy_canvas.events.mouse_move(pos=(x, y), modifiers=())
        self._vispy_canvas.events.mouse_wheel(pos=(x, y), delta=(0, 0),
                                              modifiers=())
        self._vispy_canvas.events.key_press(key=key, text=text, modifiers=())
        self._vispy_canvas.events.key_release(key=key, text=text, modifiers=())

    In most cases, if the window-cross is clicked, a native close-event is
    generated, which should then call canvas.close(). The Canvas class is
    responsible for firing the close event and calling
    backend_canvas._vispy_close, which closes the native widget.
    If this happens to result in a second close event, canvas.close() gets
    called again, but Canvas knows it is closing so it stops there.

    If canvas.close() is called (by the user), it calls
    backend_canvas._vispy_close, which closes the native widget,
    and we get the same stream of actions as above. This deviation from
    having events come from the CanvasBackend is necessitated by how
    different backends handle close events, and the various ways such
    events can be triggered.
    """

    # args are for BaseCanvasBackend, kwargs are for us.
    def __init__(self, *args, **kwargs):
        BaseCanvasBackend.__init__(self, *args)
        # We use _process_backend_kwargs() to "serialize" the kwargs
        # and to check whether they match this backend's capability
        p = self._process_backend_kwargs(kwargs)

        # Deal with config
        # ... use context.config
        # Deal with context
        p.context.shared.add_ref('backend-name', self)
        if p.context.shared.ref is self:
            self._native_context = None  # ...
        else:
            self._native_context = p.context.shared.ref._native_context

        # NativeWidgetClass.__init__(self, foo, bar)

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

    def _vispy_set_fullscreen(self, fullscreen):
        # Set the current fullscreen state
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

    def _vispy_get_fullscreen(self):
        # Should return the current fullscreen state
        raise NotImplementedError()

    def _vispy_get_native_canvas(self):
        # Should return the native widget object.
        # If this is self, this method can be omitted.
        return self


# ------------------------------------------------------------------- timer ---

class TimerBackend(BaseTimerBackend):  # Can be mixed with native timer class

    def __init__(self, vispy_timer):
        BaseTimerBackend.__init__(self, vispy_timer)

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
