# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
vispy backend for Tkinter.
"""

from __future__ import division

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend)
from ...util import keys
from ... import config

USE_EGL = config['gl_backend'].lower().startswith('es')


# -------------------------------------------------------------------- init ---

# Import
try:
    import tkinter as tk
    from OpenGL import GL
    from pyopengltk import OpenGLFrame
except:
    available, testable, why_not = False, False, "Import error"
else:
    available, testable, why_not = True, True, None


# Map native keys to vispy keys
# keysym_num -> vispy
KEYMAP = {
    65505: keys.SHIFT,
    65506: keys.SHIFT,
    65507: keys.CONTROL,
    65508: keys.CONTROL,
    65513: keys.ALT,
    65514: keys.ALT,
    65371: keys.META,
    65372: keys.META,

    65361: keys.LEFT,
    65362: keys.UP,
    65363: keys.RIGHT,
    65364: keys.DOWN,
    65365: keys.PAGEUP,
    65366: keys.PAGEDOWN,

    65379: keys.INSERT,
    65535: keys.DELETE,
    65360: keys.HOME,
    65367: keys.END,

    65307: keys.ESCAPE,
    65288: keys.BACKSPACE,

       32: keys.SPACE,
    65293: keys.ENTER,
    65289: keys.TAB,

    65470: keys.F1,
    65471: keys.F2,
    65472: keys.F3,
    65473: keys.F4,
    65474: keys.F5,
    65475: keys.F6,
    65476: keys.F7,
    65477: keys.F8,
    65478: keys.F9,
    65479: keys.F10,
    65480: keys.F11,
    65481: keys.F12,
}


# -------------------------------------------------------------- capability ---

# These are all booleans. Note that they mirror many of the kwargs to
# the initialization of the Canvas class.
capability = dict(
    # if True they mean:
    title=True,           # can set title on the fly
    size=True,            # can set size on the fly
    position=True,        # can set position on the fly
    show=True,            # can show/hide window XXX ?
    vsync=False,          # can set window to sync to blank
    resizable=True,       # can toggle resizability (e.g., no user resizing)
    decorate=True,        # can toggle decorations
    fullscreen=True,      # fullscreen window support
    context=True,         # can share contexts between windows
    multi_window=True,    # can use multiple windows at once
    scroll=True,          # scroll-wheel events are supported
    parent=True,          # can pass native widget backend parent
    always_on_top=True,   # can be made always-on-top
)


# ------------------------------------------------------- set_configuration ---
def _set_config(c):
    """Set gl configuration for template"""
    raise NotImplementedError


# ------------------------------------------------------------- application ---

_tk_toplevel = None

class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)

    def _vispy_get_backend_name(self):
        return tk.__name__

    def _vispy_process_events(self):
        app = self._vispy_get_native_app()
        app.update_idletasks()

    def _vispy_run(self):
        self._vispy_get_native_app().mainloop()

    def _vispy_quit(self):
        global _tk_toplevel
        self._vispy_get_native_app().quit()
        self._vispy_get_native_app().destroy()
        _tk_toplevel = None

    def _vispy_get_native_app(self):
        global _tk_toplevel
        if _tk_toplevel is None:
            fr = tk.Frame(None)
            _tk_toplevel = fr.master
            fr.destroy()
        return _tk_toplevel


# ------------------------------------------------------------------ canvas ---

class Coord:
    def __init__(self, tup):
        self.x, self.y = tup
        self.width, self.height = tup


# You can mix this class with the native widget
class CanvasBackend(OpenGLFrame, BaseCanvasBackend):
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

        self._double_click_supported = True

        # Deal with config
        # ... use context.config
        # Deal with context
        p.context.shared.add_ref('tkinter', self)
        if p.context.shared.ref is self:
            self._native_context = None  # ...
        else:
            self._native_context = p.context.shared.ref._native_context

        kwargs.pop("parent")
        kwargs.pop("title")
        kwargs.pop("size")
        kwargs.pop("show")
        kwargs.pop("vsync")
        kwargs.pop("resizable")
        kwargs.pop("decorate")
        kwargs.pop("always_on_top")
        kwargs.pop("fullscreen")
        kwargs.pop("context")

        if p.parent is None:
            self.top = tk.Tk()
            self.top.withdraw()

            if p.title:    self._vispy_set_title(p.title)
            if p.size:     self._vispy_set_size(p.size[0], p.size[1])
            if p.position: self._vispy_set_position(p.position[0], p.position[1])

            self.top.update_idletasks()

            if not p.resizable:
                self.top.resizable(False, False)
            if not p.decorate:
                self.top.overrideredirect(True)
            if p.always_on_top:
                self.top.wm_attributes("-topmost", "True")
            self._fullscreen = p.fullscreen

            self.top.protocol("WM_DELETE_WINDOW", self._vispy_close)
            parent = self.top
        else:
            self.top = None
            parent   = p.parent
            self._fullscreen = False

        self._init = False

        OpenGLFrame.__init__(self, parent, **kwargs)
        if not hasattr(self, "_native_context") or self._native_context is None:
            self.tkCreateContext()
            # Why can't I access __context from OpenGLFrame?
            # self._native_context = self.__context
            self._native_context = vars(self).get("_CanvasBackend__context", None)

        self.bind("<Enter>"            , self._on_mouse_enter)
        self.bind("<Motion>"           , self._on_mouse_move)
        self.bind("<MouseWheel>"       , self._on_mouse_wheel)
        self.bind("<Any-Button>"       , self._on_mouse_button_press)
        self.bind("<Double-Any-Button>", self._on_mouse_double_button_press)
        self.bind("<Any-ButtonRelease>", self._on_mouse_button_release)
        self.bind("<Configure>"        , self._on_configure, add='+')
        # self.bind("<Expose>"           , self.redraw)
        # self.bind("<Map>"              , self.redraw)
        self.bind("<Any-KeyPress>"     , self._on_key_down)
        self.bind("<Any-KeyRelease>"   , self._on_key_up)

        self._vispy_set_visible(p.show)
        self.focus_force()

    def initgl(self):
        # For the user code
        self.update_idletasks()

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glClearColor(0.0, 0.0, 0.0, 0.0)

        # self.set_update_interval(16)  # Auto start rendering at ~60 FPS?

    def redraw(self, *args):
        # For the user code
        if self._vispy_canvas is None:
            return
        if not self._init:
            self._initialize()
        self._vispy_canvas.set_current()
        self._vispy_canvas.events.draw(region=None)

    def set_update_interval(self, interval_ms=17):
        self.animate = interval_ms
        self.tkExpose(None)

    def _on_configure(self, e):
        if self._vispy_canvas is None or not self._init:
            return
        self._vispy_canvas.events.resize(size=(e.width, e.height))

    def _initialize(self):
        print("_initialize")
        self.initgl()

        if self._vispy_canvas is None:
            return
        self._init = True
        self._vispy_canvas.set_current()
        self._vispy_canvas.events.initialize()
        self.update_idletasks()
        self._on_configure(Coord(self._vispy_get_size()))

    STATE_LUT = {
        0x0001: keys.SHIFT,
        # 0x0002: CAPSLOCK,
        0x0004: keys.CONTROL,
        # 0x0008: keys.ALT,  # LEFT_ALT: Seems always pressed?
        # 0x0010: NUMLOCK,
        # 0x0020: SCROLLLOCK,
        0x0080: keys.ALT,
        # 0x0100: ?,  # Mouse button 1.
        # 0x0200: ?,  # Mouse button 2.
        # 0x0400: ?,  # Mouse button 3.
        0x20000: keys.ALT  # LEFT_ALT ?
    }

    def _parse_state(self, e):
        return [ key for mask, key in self.STATE_LUT.items() \
                    if e.state & mask]

    def _parse_keys(self, e):
        if e.keysym_num in KEYMAP:
            return KEYMAP[e.keysym_num], ""
        # e.char, e.keycode, e.keysym, e.keysym_num
        key = e.keycode
        if 97 <= key <= 122:
            key -= 32
        if key >= 32 and key <= 127:
            return keys.Key(chr(key)), chr(key)
        else:
            return None, None

    def _on_mouse_enter(self, e):
        if self._vispy_canvas is None:
            return
        self._vispy_mouse_move(
            pos=(e.x, e.y), modifiers=self._parse_state(e))

    def _on_mouse_move(self, e):
        if self._vispy_canvas is None:
            return
        self._vispy_mouse_move(
            pos=(e.x, e.y), modifiers=self._parse_state(e))

    def _on_mouse_wheel(self, e):
        if self._vispy_canvas is None:
            return
        # e.num: 4 when up, 5 when down (only on *nix?)
        # Scroll up  : e.delta > 0
        # Scroll down: e.delta < 0
        self._vispy_canvas.events.mouse_wheel(
            delta=(0.0, float(e.delta / 120)),
            pos=(e.x, e.y), modifiers=self._parse_state(e))

    def _on_mouse_button_press(self, e):
        if self._vispy_canvas is None:
            return
        # [ left=1, middle, right]
        btn = { 1:1, 2:3, 3:2}
        self._vispy_mouse_press(
            pos=(e.x, e.y), button=btn[e.num], modifiers=self._parse_state(e))

    def _vispy_detect_double_click(self, e):
        # Override base class function
        # since double click handling is native in Tk.
        pass

    def _on_mouse_double_button_press(self, e):
        if self._vispy_canvas is None:
            return
        # [ left=1, middle, right]
        btn = { 1:1, 2:3, 3:2}
        self._vispy_mouse_double_click(
            pos=(e.x, e.y), button=btn[e.num], modifiers=self._parse_state(e))

    def _on_mouse_button_release(self, e):
        if self._vispy_canvas is None:
            return
        # [ left=1, middle, right]
        btn = { 1:1, 2:3, 3:2}
        self._vispy_mouse_release(
            pos=(e.x, e.y), button=btn[e.num], modifiers=self._parse_state(e))

    def _on_key_down(self, e):
        if self._vispy_canvas is None:
            return
        key, text = self._parse_keys(e)
        self._vispy_canvas.events.key_press(
            key=key, text=text, modifiers=self._parse_state(e))

    def _on_key_up(self, e):
        if self._vispy_canvas is None:
            return
        key, text = self._parse_keys(e)
        self._vispy_canvas.events.key_release(
            key=key, text=text, modifiers=self._parse_state(e))

    def _vispy_set_current(self):
        # Make this the current context
        self.tkMakeCurrent()

    def _vispy_swap_buffers(self):
        # Swap front and back buffer
        self._vispy_canvas.set_current()
        # self.tkSwapBuffers()

    def _vispy_set_title(self, title):
        # Set the window title. Has no effect for widgets
        if self.top:
            self.top.title(title)

    def _vispy_set_size(self, w, h):
        # Set size of the widget or window
        if self.top:
            self.top.geometry(f"{w}x{h}")

    def _vispy_set_position(self, x, y):
        # Set location of the widget or window. May have no effect for widgets
        if self.top:
            self.top.geometry(f"+{x}+{y}")

    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        if self.top:
            if visible:
                self.top.wm_deiconify()
                self.top.lift()
                self.top.attributes('-fullscreen', self._fullscreen)
            else:
                self.top.withdraw()

    def _vispy_set_fullscreen(self, fullscreen):
        # Set the current fullscreen state
        self._fullscreen = bool(fullscreen)
        if self.top:
            self._vispy_set_visible(True)

    def _vispy_update(self):
        # Invoke a redraw
        self.set_update_interval(0)

    def _vispy_close(self):
        # Force the window or widget to shut down
        if self.top:
            self._vispy_canvas.close()
            self.destroy()

    def _vispy_get_size(self):
        # Should return widget size
        if self.top: self.top.update_idletasks()
        return self.winfo_width(), self.winfo_height()

    def _vispy_get_position(self):
        # Should return widget position
        return self.winfo_x(), self.winfo_y()

    def _vispy_get_fullscreen(self):
        # Should return the current fullscreen state
        return self._fullscreen

    def _vispy_get_native_canvas(self):
        # Should return the native widget object.
        # If this is self, this method can be omitted.
        return self


# ------------------------------------------------------------------- timer ---

class TimerBackend(BaseTimerBackend):  # Can be mixed with native timer class

    def __init__(self, vispy_timer):
        BaseTimerBackend.__init__(self, vispy_timer)
        global _tk_toplevel
        if _tk_toplevel is None:
            raise Exception("TimerBackend: No toplevel?")
        self._tk = _tk_toplevel
        self._id = None
        self.last_interval = 1

    def _vispy_start(self, interval):
        self._vispy_stop()
        self.last_interval = int(round(interval * 1000))
        self._id = self._tk.after(self.last_interval, self._vispy_timeout)

    def _vispy_stop(self):
        if self._id is not None:
            self._tk.after_cancel(self._id)
            self._id = None

    def _vispy_timeout(self):
        self._vispy_timer._timeout()
        self._id = self._tk.after(self.last_interval, self._vispy_timeout)

    def _vispy_get_native_timer(self):
        # Should return the native widget object.
        # If this is self, this method can be omitted.
        return self
