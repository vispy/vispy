# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""vispy backend for pyglet."""

from __future__ import division

from packaging.version import Version
from time import sleep

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend)
from ...util import keys
from ...util.ptime import time
from ... import config

USE_EGL = config['gl_backend'].lower().startswith('es')


# -------------------------------------------------------------------- init ---

try:
    import pyglet
    version = pyglet.version
    if Version(version) < Version('1.2'):
        help_ = ('You can install the latest pyglet using:\n    '
                 'pip install http://pyglet.googlecode.com/archive/tip.zip')
        raise ImportError('Pyglet version too old (%s), need >= 1.2\n%s'
                          % (version, help_))

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
except Exception as exp:
    available, testable, why_not, which = False, False, str(exp), None

    class _Window(object):
        pass
else:
    if USE_EGL:
        available, testable, why_not = False, False, 'EGL not supported'
    else:
        available, testable, why_not = True, True, None
    which = 'pyglet ' + str(pyglet.version)
    _Window = pyglet.window.Window


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
    always_on_top=False,
)


# ------------------------------------------------------- set_configuration ---

def _set_config(config):
    """Set gl configuration"""
    pyglet_config = pyglet.gl.Config()

    pyglet_config.red_size = config['red_size']
    pyglet_config.green_size = config['green_size']
    pyglet_config.blue_size = config['blue_size']
    pyglet_config.alpha_size = config['alpha_size']

    pyglet_config.accum_red_size = 0
    pyglet_config.accum_green_size = 0
    pyglet_config.accum_blue_size = 0
    pyglet_config.accum_alpha_size = 0

    pyglet_config.depth_size = config['depth_size']
    pyglet_config.stencil_size = config['stencil_size']
    pyglet_config.double_buffer = config['double_buffer']
    pyglet_config.stereo = config['stereo']
    pyglet_config.samples = config['samples']
    return pyglet_config


# ------------------------------------------------------------- application ---

class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)

    def _vispy_get_backend_name(self):
        return 'Pyglet'

    def _vispy_process_events(self):
        # pyglet.app.platform_event_loop.step(0.0)
        pyglet.clock.tick()
        for window in pyglet.app.windows:
            window.switch_to()
            window.dispatch_events()
            window.dispatch_event('on_draw')

    def _vispy_run(self):
        return pyglet.app.run()

    def _vispy_quit(self):
        return pyglet.app.exit()

    def _vispy_get_native_app(self):
        return pyglet.app


# ------------------------------------------------------------------ canvas ---

class CanvasBackend(BaseCanvasBackend, _Window):
    """Pyglet backend for Canvas abstract class."""

    def __init__(self, vispy_canvas, **kwargs):
        BaseCanvasBackend.__init__(self, vispy_canvas)
        p = self._process_backend_kwargs(kwargs)

        # Deal with config
        config = _set_config(p.context.config)  # Also used further below
        # Deal with context
        p.context.shared.add_ref('pyglet', self)
        # contexts are shared by default in Pyglet

        style = (pyglet.window.Window.WINDOW_STYLE_DEFAULT if p.decorate else
                 pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
        # We keep track of modifier keys so we can pass them to mouse_motion
        self._current_modifiers = set()
        # self._buttons_accepted = 0
        self._draw_ok = False  # whether it is ok to draw yet
        self._pending_position = None
        if p.fullscreen is not False:
            screen = pyglet.window.get_platform().get_default_display()
            self._vispy_fullscreen = True
            if p.fullscreen is True:
                self._vispy_screen = screen.get_default_screen()
            else:
                screen = screen.get_screens()
                if p.fullscreen >= len(screen):
                    raise RuntimeError('fullscreen must be < %s'
                                       % len(screen))
                self._vispy_screen = screen[p.fullscreen]
        else:
            self._vispy_fullscreen = False
            self._vispy_screen = None
        self._initialize_sent = False
        pyglet.window.Window.__init__(self, width=p.size[0], height=p.size[1],
                                      caption=p.title, visible=p.show,
                                      config=config, vsync=p.vsync,
                                      resizable=p.resizable, style=style,
                                      screen=self._vispy_screen)
        if p.position is not None:
            self._vispy_set_position(*p.position)

    def _vispy_warmup(self):
        etime = time() + 0.1
        while time() < etime:
            sleep(0.01)
            self._vispy_canvas.set_current()
            self._vispy_canvas.app.process_events()

    # Override these ...
    def flip(self):
        # Is called by event loop after each draw
        pass

    def on_draw(self):
        # Is called by event loop after each event, whatever event ... really
        if not self._draw_ok:
            self._draw_ok = True
            self.our_draw_func()

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
        pyglet.clock.schedule_once(self.our_draw_func, 0.0)

    def _vispy_close(self):
        # Force the window or widget to shut down
        # In Pyglet close is equivalent to destroy (window becomes invalid)
        self._vispy_canvas = None
        self.close()

    def _vispy_get_size(self):
        w, h = self.get_size()
        return w, h

    def _vispy_get_physical_size(self):
        if self._vispy_canvas is None:
            return
        w, h = self.get_framebuffer_size()
        return w, h

    def _vispy_get_position(self):
        x, y = self.get_location()
        return x, y

    def _vispy_get_fullscreen(self):
        return self._vispy_fullscreen

    def _vispy_set_fullscreen(self, fullscreen):
        self._vispy_fullscreen = bool(fullscreen)
        self.set_fullscreen(self._vispy_fullscreen, self._vispy_screen)

    def on_show(self):
        if self._vispy_canvas is None:
            return
        if not self._initialize_sent:
            self._initialize_sent = True
            self._vispy_canvas.set_current()
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
        self._vispy_canvas.close()

    def on_resize(self, w, h):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.resize(size=(w, h))
        # self._vispy_update()

    def our_draw_func(self, dummy=None):
        if not self._draw_ok or self._vispy_canvas is None:
            return
        # (0, 0, self.width, self.height))
        self._vispy_canvas.set_current()
        self._vispy_canvas.events.draw(region=None)

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
            # self._buttons_accepted &= ~button

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
            pos=(x, self.get_size()[1] - y),
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


# ------------------------------------------------------------------- timer ---

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
