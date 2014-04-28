# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
vispy backend for sdl2.
"""

from __future__ import division

import atexit
import ctypes
from time import sleep

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend, BaseSharedContext)
from ...util import keys, logger
from ...util.ptime import time


# -------------------------------------------------------------------- init ---

try:
    import sdl2
    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0:  # only ever call once
        raise OSError('Could not init sdl2: %s' % sdl2.SDL_GetError())
    atexit.register(sdl2.SDL_Quit)

    # Map native keys to vispy keys
    KEYMAP = {
        # http://www.ginkgobitter.org/sdl/?SDL_Keycode
        sdl2.SDLK_LSHIFT: keys.SHIFT,
        sdl2.SDLK_RSHIFT: keys.SHIFT,
        sdl2.SDLK_LCTRL: keys.CONTROL,
        sdl2.SDLK_RCTRL: keys.CONTROL,
        sdl2.SDLK_LALT: keys.ALT,
        sdl2.SDLK_RALT: keys.ALT,
        sdl2.SDLK_LGUI: keys.META,
        sdl2.SDLK_RGUI: keys.META,

        sdl2.SDLK_LEFT: keys.LEFT,
        sdl2.SDLK_UP: keys.UP,
        sdl2.SDLK_RIGHT: keys.RIGHT,
        sdl2.SDLK_DOWN: keys.DOWN,
        sdl2.SDLK_PAGEUP: keys.PAGEUP,
        sdl2.SDLK_PAGEDOWN: keys.PAGEDOWN,

        sdl2.SDLK_INSERT: keys.INSERT,
        sdl2.SDLK_DELETE: keys.DELETE,
        sdl2.SDLK_HOME: keys.HOME,
        sdl2.SDLK_END: keys.END,

        sdl2.SDLK_ESCAPE: keys.ESCAPE,
        sdl2.SDLK_BACKSPACE: keys.BACKSPACE,

        sdl2.SDLK_F1: keys.F1,
        sdl2.SDLK_F2: keys.F2,
        sdl2.SDLK_F3: keys.F3,
        sdl2.SDLK_F4: keys.F4,
        sdl2.SDLK_F5: keys.F5,
        sdl2.SDLK_F6: keys.F6,
        sdl2.SDLK_F7: keys.F7,
        sdl2.SDLK_F8: keys.F8,
        sdl2.SDLK_F9: keys.F9,
        sdl2.SDLK_F10: keys.F10,
        sdl2.SDLK_F11: keys.F11,
        sdl2.SDLK_F12: keys.F12,

        sdl2.SDLK_SPACE: keys.SPACE,
        sdl2.SDLK_RETURN: keys.ENTER,
        sdl2.SDLK_TAB: keys.TAB,
    }

    BUTTONMAP = {sdl2.SDL_BUTTON_LEFT: 1,
                 sdl2.SDL_BUTTON_MIDDLE: 2,
                 sdl2.SDL_BUTTON_RIGHT: 3
                 }
except Exception as exp:
    available, testable, why_not, which = False, False, str(exp), None
else:
    available, testable, why_not = True, True, None
    which = 'sdl2 %d.%d.%d' % sdl2.version_info[:3]

_VP_SDL2_ALL_WINDOWS = {}


def _get_sdl2_windows():
    return list(_VP_SDL2_ALL_WINDOWS.values())


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
)


# ------------------------------------------------------- set_configuration ---

def _set_config(c):
    """Set gl configuration for SDL2"""
    func = sdl2.SDL_GL_SetAttribute
    func(sdl2.SDL_GL_RED_SIZE, c['red_size'])
    func(sdl2.SDL_GL_GREEN_SIZE, c['green_size'])
    func(sdl2.SDL_GL_BLUE_SIZE, c['blue_size'])
    func(sdl2.SDL_GL_ALPHA_SIZE, c['alpha_size'])
    func(sdl2.SDL_GL_DEPTH_SIZE, c['depth_size'])
    func(sdl2.SDL_GL_STENCIL_SIZE, c['stencil_size'])
    samps = c['samples']
    func(sdl2.SDL_GL_MULTISAMPLEBUFFERS, 1 if samps > 0 else 0)
    func(sdl2.SDL_GL_MULTISAMPLESAMPLES, samps if samps > 0 else 0)
    func(sdl2.SDL_GL_STEREO, c['stereo'])


class SharedContext(BaseSharedContext):
    _backend = 'sdl2'


# ------------------------------------------------------------- application ---

class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)
        self._timers = list()

    def _add_timer(self, timer):
        if timer not in self._timers:
            self._timers.append(timer)

    def _vispy_get_backend_name(self):
        return 'SDL2'

    def _vispy_process_events(self):
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            _id = event.window.windowID
            if _id in _VP_SDL2_ALL_WINDOWS:
                win = _VP_SDL2_ALL_WINDOWS[_id]
                win._on_event(event)
        for timer in self._timers:
            timer._tick()
        wins = _get_sdl2_windows()
        for win in wins:
            if win._needs_draw:
                win._needs_draw = False
                win._on_draw()

    def _vispy_run(self):
        wins = _get_sdl2_windows()
        while all(w._id is not None for w in wins):
            self._vispy_process_events()
        self._vispy_quit()  # to clean up

    def _vispy_quit(self):
        # Close windows
        wins = _get_sdl2_windows()
        for win in wins:
            win._vispy_close()
        # tear down timers
        for timer in self._timers:
            timer._vispy_stop()
        self._timers = []

    def _vispy_get_native_app(self):
        return sdl2


# ------------------------------------------------------------------ canvas ---

class CanvasBackend(BaseCanvasBackend):

    """ SDL2 backend for Canvas abstract class."""

    def __init__(self, **kwargs):
        BaseCanvasBackend.__init__(self, capability, SharedContext)
        title, size, position, show, vsync, resize, dec, fs, context = \
            self._process_backend_kwargs(kwargs)
        # Init SDL2, add window hints, and create window
        if isinstance(context, dict):
            _set_config(context)
            share = None
        else:
            share = context.value
            sdl2.SDL_GL_MakeCurrent(*share)  # old window must be current
            sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_SHARE_WITH_CURRENT_CONTEXT, 1)

        sdl2.SDL_GL_SetSwapInterval(1 if vsync else 0)
        flags = sdl2.SDL_WINDOW_OPENGL
        flags |= sdl2.SDL_WINDOW_SHOWN  # start out shown
        flags |= sdl2.SDL_WINDOW_ALLOW_HIGHDPI
        flags |= sdl2.SDL_WINDOW_RESIZABLE if resize else 0
        flags |= sdl2.SDL_WINDOW_BORDERLESS if not dec else 0
        if fs is not False:
            if isinstance(fs, int):
                logger.warn('Cannot specify monitor number for SDL2 '
                            'fullscreen, using default')
            flags |= sdl2.SDL_WINDOW_FULLSCREEN
        self._mods = list()
        if position is None:
            position = [sdl2.SDL_WINDOWPOS_UNDEFINED] * 2
        self._id = sdl2.SDL_CreateWindow(title.encode('UTF-8'),
                                         position[0], position[1],
                                         size[0], size[1], flags)
        if not self._id:
            raise RuntimeError('Could not create window')
        if share is None:
            self._native_context = sdl2.SDL_GL_CreateContext(self._id)
        else:
            self._native_context = sdl2.SDL_GL_CreateContext(share[0])
        self._sdl_id = sdl2.SDL_GetWindowID(self._id)
        _VP_SDL2_ALL_WINDOWS[self._sdl_id] = self
        self._vispy_canvas_ = None
        self._needs_draw = False
        self._vispy_set_current()
        if not show:
            self._vispy_set_visible(False)

    @property
    def _vispy_context(self):
        """Context to return for sharing"""
        return SharedContext((self._id, self._native_context))

    ####################################
    # Deal with events we get from vispy
    @property
    def _vispy_canvas(self):
        """ The parent canvas/window """
        return self._vispy_canvas_

    @_vispy_canvas.setter
    def _vispy_canvas(self, vc):
        # Init events when the property is set by Canvas
        self._vispy_canvas_ = vc
        if vc is not None:
            self._vispy_set_current()
            self._vispy_canvas.events.initialize()
        return self._vispy_canvas

    def _vispy_warmup(self):
        etime = time() + 0.1
        while time() < etime:
            sleep(0.01)
            self._vispy_set_current()
            self._vispy_canvas.app.process_events()

    def _vispy_set_current(self):
        if self._id is None:
            return
        # Make this the current context
        sdl2.SDL_GL_MakeCurrent(self._id, self._native_context)

    def _vispy_swap_buffers(self):
        if self._id is None:
            return
        # Swap front and back buffer
        sdl2.SDL_GL_SwapWindow(self._id)

    def _vispy_set_title(self, title):
        if self._id is None:
            return
        # Set the window title. Has no effect for widgets
        sdl2.SDL_SetWindowTitle(self._id, title.encode('UTF-8'))

    def _vispy_set_size(self, w, h):
        if self._id is None:
            return
        # Set size of the widget or window
        sdl2.SDL_SetWindowSize(self._id, w, h)

    def _vispy_set_position(self, x, y):
        if self._id is None:
            return
        # Set position of the widget or window. May have no effect for widgets
        sdl2.SDL_SetWindowPosition(self._id, x, y)

    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        if self._id is None:
            return
        if visible:
            sdl2.SDL_ShowWindow(self._id)
            # this ensures that the show takes effect
            self._vispy_update()
        else:
            sdl2.SDL_HideWindow(self._id)

    def _vispy_update(self):
        # Invoke a redraw, passing it on to the canvas
        if self._vispy_canvas is None or self._id is None:
            return
        # Mark that this window wants to be painted on the next loop iter
        self._needs_draw = True

    def _vispy_close(self):
        # Force the window or widget to shut down
        if self._id is not None:
            _id = self._id
            self._id = None
            sdl2.SDL_DestroyWindow(_id)
            del _VP_SDL2_ALL_WINDOWS[self._sdl_id]
            self._sdl_id = None

    def _vispy_get_size(self):
        if self._id is None:
            return
        w, h = ctypes.c_int(), ctypes.c_int()
        sdl2.SDL_GetWindowSize(self._id, ctypes.byref(w), ctypes.byref(h))
        w, h = w.value, h.value
        return w, h

    def _vispy_get_position(self):
        if self._id is None:
            return
        x, y = ctypes.c_int(), ctypes.c_int()
        sdl2.SDL_GetWindowPosition(self._id, ctypes.byref(x), ctypes.byref(y))
        x, y = x.value, y.value
        return x, y

    ##########################################
    # Notify vispy of events triggered by SDL2
    def _get_mouse_position(self):
        if self._id is None:
            return (0, 0)
        x, y = ctypes.c_int(), ctypes.c_int()
        sdl2.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
        return x.value, y.value

    def _on_draw(self):
        if self._vispy_canvas is None or self._id is None:
            return
        self._vispy_set_current()
        self._vispy_canvas.events.paint(region=None)  # (0, 0, w, h))

    def _on_event(self, event):
        if self._vispy_canvas is None:
            return
        # triage event to proper handler
        if event.type == sdl2.SDL_QUIT:
            self._vispy_canvas.events.close()
        elif event.type == sdl2.SDL_WINDOWEVENT:
            if event.window.event == sdl2.SDL_WINDOWEVENT_RESIZED:
                w, h = event.window.data1, event.window.data2
                self._vispy_canvas.events.resize(size=(w, h))
            elif event.window.event == sdl2.SDL_WINDOWEVENT_CLOSE:
                self._vispy_canvas.events.close()
        elif event.type == sdl2.SDL_MOUSEMOTION:
            x, y = event.motion.x, event.motion.y
            self._vispy_mouse_move(pos=(x, y), modifiers=self._mods)
        elif event.type in (sdl2.SDL_MOUSEBUTTONDOWN,
                            sdl2.SDL_MOUSEBUTTONUP):
            x, y = event.button.x, event.button.y
            button = event.button.button
            if button in BUTTONMAP:
                button = BUTTONMAP.get(button, 0)
                if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    func = self._vispy_mouse_press
                else:
                    func = self._vispy_mouse_release
                func(pos=(x, y), button=button, modifiers=self._mods)
        elif event.type == sdl2.SDL_MOUSEWHEEL:
            pos = self._get_mouse_position()
            delta = float(event.wheel.x), float(event.wheel.y)
            self._vispy_canvas.events.mouse_wheel(pos=pos, delta=delta,
                                                  modifiers=self._mods)
        elif event.type in (sdl2.SDL_KEYDOWN, sdl2.SDL_KEYUP):
            down = (event.type == sdl2.SDL_KEYDOWN)
            keysym = event.key.keysym
            mods = keysym.mod
            key = keysym.sym
            self._process_mod(mods, down)
            if key in KEYMAP:
                key = KEYMAP[key]
                if down:
                    fun = self._vispy_canvas.events.key_press
                else:
                    fun = self._vispy_canvas.events.key_release
                fun(key=key, text='', modifiers=self._mods)

    def _process_mod(self, key, down):
        _modifiers = list()
        if key & (sdl2.SDLK_LSHIFT | sdl2.SDLK_RSHIFT):
            _modifiers.append(keys.SHIFT)
        if key & (sdl2.SDLK_LCTRL | sdl2.SDLK_RCTRL):
            _modifiers.append(keys.CONTROL)
        if key & (sdl2.SDLK_LALT | sdl2.SDLK_RALT):
            _modifiers.append(keys.ALT)
        if key & (sdl2.SDLK_LGUI | sdl2.SDLK_RGUI):
            _modifiers.append(keys.META)
        for mod in _modifiers:
            if mod not in self._mods:
                if down:
                    self._mods.append(mod)
            elif not down:
                self._mods.pop(self._mods.index(mod))

# ------------------------------------------------------------------- timer ---


# XXX should probably use SDL_Timer (and SDL_INIT_TIMER)

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
