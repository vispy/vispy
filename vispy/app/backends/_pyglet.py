# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
vispy backend for pyglet.
"""

# absolute import is important here, since this module is called pyglet :)
from __future__ import division

import pyglet.window
import pyglet.app
import pyglet.clock

from ..base import BaseApplicationBackend, BaseCanvasBackend, BaseTimerBackend
from ...util import keys


# Map native keys to vispy keys
KEYMAP = {
    pyglet.window.key.LSHIFT: keys.SHIFT,
    pyglet.window.key.RSHIFT: keys.SHIFT,
    pyglet.window.key.LCTRL: keys.CONTROL,
    pyglet.window.key.RCTRL: keys.CONTROL,
    pyglet.window.key.LALT: keys.ALT,
    pyglet.window.key.RALT: keys.ALT,
    pyglet.window.key.LMETA: keys.META,
    pyglet.window.key.RMETA: keys.META,

    pyglet.window.key.LEFT: keys.LEFT,
    pyglet.window.key.UP: keys.UP,
    pyglet.window.key.RIGHT: keys.RIGHT,
    pyglet.window.key.DOWN: keys.DOWN,
    pyglet.window.key.PAGEUP: keys.PAGEUP,
    pyglet.window.key.PAGEDOWN: keys.PAGEDOWN,

    pyglet.window.key.INSERT: keys.INSERT,
    pyglet.window.key.DELETE: keys.DELETE,
    pyglet.window.key.HOME: keys.HOME,
    pyglet.window.key.END: keys.END,

    pyglet.window.key.ESCAPE: keys.ESCAPE,
    pyglet.window.key.BACKSPACE: keys.BACKSPACE,

    pyglet.window.key.F1: keys.F1,
    pyglet.window.key.F2: keys.F2,
    pyglet.window.key.F3: keys.F3,
    pyglet.window.key.F4: keys.F4,
    pyglet.window.key.F5: keys.F5,
    pyglet.window.key.F6: keys.F6,
    pyglet.window.key.F7: keys.F7,
    pyglet.window.key.F8: keys.F8,
    pyglet.window.key.F9: keys.F9,
    pyglet.window.key.F10: keys.F10,
    pyglet.window.key.F11: keys.F11,
    pyglet.window.key.F12: keys.F12,

    pyglet.window.key.SPACE: keys.SPACE,
    pyglet.window.key.ENTER: keys.ENTER,  # == pyglet.window.key.RETURN
    pyglet.window.key.NUM_ENTER: keys.ENTER,
    pyglet.window.key.TAB: keys.TAB,
}


BUTTONMAP = {pyglet.window.mouse.LEFT: 1,
             pyglet.window.mouse.RIGHT: 2,
             pyglet.window.mouse.MIDDLE: 3
             }


class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)

    def _vispy_get_backend_name(self):
        return 'Pyglet'

    def _vispy_process_events(self):
        return pyglet.app.platform_event_loop.step(0.0)

    def _vispy_run(self):
        return pyglet.app.run()

    def _vispy_quit(self):
        return pyglet.app.exit()

    def _vispy_get_native_app(self):
        return pyglet.app


class CanvasBackend(pyglet.window.Window, BaseCanvasBackend):

    """ Pyglet backend for Canvas abstract class."""

    def __init__(self, *args, **kwargs):
        BaseCanvasBackend.__init__(self)
        # Initialize native widget, but default hidden and resizable
        kwargs['visible'] = kwargs.get('visible', False)
        kwargs['resizable'] = kwargs.get('resizable', True)
        kwargs['vsync'] = kwargs.get('vsync', 0)
        pyglet.window.Window.__init__(self, *args, **kwargs)

        # We keep track of modifier keys so we can pass them to mouse_motion
        self._current_modifiers = set()
        #self._buttons_accepted = 0
        self._draw_ok = False  # whether it is ok to draw yet
        self._pending_position = None

    # Override these ...
    def flip(self):
        # Is called by event loop after each draw
        pass

    def on_draw(self):
        # Is called by event loop after each event, whatever event ... really
        if not self._draw_ok:
            self._draw_ok = True
            self.our_paint_func()

    def draw_mouse_cursor(self):
        # Prevent legacy OpenGL
        pass

    def _vispy_set_current(self):
        # Make this the current context
        self.switch_to()

    def _vispy_swap_buffers(self):
        # Swap front and back buffer
        pyglet.window.Window.flip(self)

    def _vispy_set_title(self, title):
        # Set the window title. Has no effect for widgets
        self.set_caption(title)

    def _vispy_set_size(self, w, h):
        # Set size of the widget or window
        self.set_size(w, h)

    def _vispy_set_position(self, x, y):
        # Set positionof the widget or window. May have no effect for widgets
        if self._draw_ok:
            self.set_location(x, y)
        else:
            self._pending_position = x, y

    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        self.set_visible(visible)

    def _vispy_update(self):
        # Invoke a redraw
        pyglet.clock.schedule_once(self.our_paint_func, 0.0)

    def _vispy_close(self):
        # Force the window or widget to shut down
        self.close()

    def _vispy_get_size(self):
        x, y = self.get_size()
        return x, y

    def _vispy_get_position(self):
        w, h = self.get_location()
        return w, h

    def on_show(self):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.initialize()
        # Set location now if we must. For some reason we get weird
        # offsets in viewport if set_location is called before the
        # widget is shown.
        if self._pending_position:
            x, y = self._pending_position
            self._pending_position = None
            self.set_location(x, y)
        # Redraw
        self._vispy_update()

    def on_close(self):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.close()
        self.close()  # Or the window wont close

    def on_resize(self, w, h):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.resize(size=(w, h))
        # self._vispy_update()

    def our_paint_func(self, dummy=None):
        if not self._draw_ok or self._vispy_canvas is None:
            return
        # (0, 0, self.width, self.height))
        self._vispy_canvas.events.paint(region=None)

    def on_mouse_press(self, x, y, button, modifiers=None):
        if self._vispy_canvas is None:
            return
        self._vispy_mouse_press(
            pos=(x, self.get_size()[1] - y),
            button=BUTTONMAP.get(button, 0),
            modifiers=self._modifiers(),
        )
#         if ev2.handled:
#             self._buttons_accepted |= button

    def on_mouse_release(self, x, y, button, modifiers=None):
        if self._vispy_canvas is None:
            return
        if True:  # (button & self._buttons_accepted) > 0:
            self._vispy_mouse_release(
                pos=(x, self.get_size()[1] - y),
                button=BUTTONMAP.get(button, 0),
                modifiers=self._modifiers(),
            )
            #self._buttons_accepted &= ~button

    def on_mouse_motion(self, x, y, dx, dy):
        if self._vispy_canvas is None:
            return
        self._vispy_mouse_move(
            pos=(x, self.get_size()[1] - y),
            modifiers=self._modifiers(),
        )

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.mouse_wheel(
            delta=(float(scroll_x), float(scroll_y)),
            pos=(x, y),
            modifiers=self._modifiers(),
        )

    def on_key_press(self, key, modifiers):
        # Process modifiers
        if key in (pyglet.window.key.LCTRL, pyglet.window.key.RCTRL,
                   pyglet.window.key.LALT, pyglet.window.key.RALT,
                   pyglet.window.key.LSHIFT, pyglet.window.key.RSHIFT):
            self._current_modifiers.add(key)
        # Emit
        self._vispy_canvas.events.key_press(
            key=self._processKey(key),
            text='',  # Handlers that trigger on text wont see this event
            modifiers=self._modifiers(modifiers))

    def on_text(self, text):
        # Typically this is called after on_key_press and before
        # on_key_release
        self._vispy_canvas.events.key_press(
            key=None,  # Handlers that trigger on key wont see this event
            text=text,
            modifiers=self._modifiers())

    def on_key_release(self, key, modifiers):
        # Process modifiers
        if key in (pyglet.window.key.LCTRL, pyglet.window.key.RCTRL,
                   pyglet.window.key.LALT, pyglet.window.key.RALT,
                   pyglet.window.key.LSHIFT, pyglet.window.key.RSHIFT):
            self._current_modifiers.discard(key)
        # Get txt
        try:
            text = chr(key)
        except Exception:
            text = ''
        # Emit
        self._vispy_canvas.events.key_release(
            key=self._processKey(key), text=text,
            modifiers=self._modifiers(modifiers))

    def _processKey(self, key):
        if 97 <= key <= 122:
            key -= 32
        if key in KEYMAP:
            return KEYMAP[key]
        elif key >= 32 and key <= 127:
            return keys.Key(chr(key))
        else:
            return None

    def _modifiers(self, pygletmod=None):
        mod = ()
        if pygletmod is None:
            pygletmod = self._current_modifiers
        if isinstance(pygletmod, set):
            for key in pygletmod:
                mod += KEYMAP[key],
        else:
            if pygletmod & pyglet.window.key.MOD_SHIFT:
                mod += keys.SHIFT,
            if pygletmod & pyglet.window.key.MOD_CTRL:
                mod += keys.CONTROL,
            if pygletmod & pyglet.window.key.MOD_ALT:
                mod += keys.ALT,
        return mod


class TimerBackend(BaseTimerBackend):

    def _vispy_start(self, interval):
        interval = self._vispy_timer._interval
        if self._vispy_timer.max_iterations == 1:
            pyglet.clock.schedule_once(self._vispy_timer._timeout, interval)
        else:
            # seems pyglet does not give the expected behavior when interval==0
            if interval == 0:
                interval = 1e-9
            pyglet.clock.schedule_interval(
                self._vispy_timer._timeout,
                interval)

    def _vispy_stop(self):
        pyglet.clock.unschedule(self._vispy_timer._timeout)

    def _vispy_get_native_timer(self):
        return pyglet.clock
