# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""vispy backend for Tkinter."""

from __future__ import division

from time import sleep
import warnings

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend)
from ...util import keys
from ...util.ptime import time
from ...gloo import gl

# -------------------------------------------------------------------- init ---

# Import
try:
    import sys

    _tk_on_linux, _tk_on_darwin, _tk_on_windows = \
        map(sys.platform.startswith, ("linux", "darwin", "win"))
    _tk_pyopengltk_imported = False

    import tkinter as tk
    import pyopengltk
except (ModuleNotFoundError, ImportError):
    available, testable, why_not, which = \
        False, False, "Could not import Tkinter or pyopengltk, module(s) not found.", None
else:
    which_pyopengltk = getattr(pyopengltk, "__version__", "???")
    which = f"Tkinter {tk.TkVersion} (with pyopengltk {which_pyopengltk})"

    if hasattr(pyopengltk, "OpenGLFrame"):
        _tk_pyopengltk_imported = True
        available, testable, why_not = True, True, None
    else:
        # pyopengltk does not provide an implementation for this platform
        available, testable, why_not = \
            False, False, f"pyopengltk {which_pyopengltk} is not supported on this platform ({sys.platform})!"

if _tk_pyopengltk_imported:
    # Put OpenGLFrame class in global namespace
    OpenGLFrame = pyopengltk.OpenGLFrame
else:
    # Create empty placeholder class
    class OpenGLFrame(object):
        pass

# Map native keys to vispy keys
# e.keysym_num -> vispy
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

# e.state -> vispy
KEY_STATE_MAP = {
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

# e.num -> vispy
MOUSE_BUTTON_MAP = {
    1: 1,  # Mouse Left   == 1 -> Mouse Left
    2: 3,  # Mouse Middle == 2 -> Mouse Middle
    3: 2,  # Mouse Right  == 3 -> Mouse Right

    # TODO: If other mouse buttons are needed
    # and they differ from the Tkinter numbering, add them here.
    # e.g. BACK/FORWARD buttons or other custom mouse buttons
}

# -------------------------------------------------------------- capability ---

# These are all booleans. Note that they mirror many of the kwargs to
# the initialization of the Canvas class.
capability = dict(
    # if True they mean:
    title=True,           # can set title on the fly
    size=True,            # can set size on the fly
    position=True,        # can set position on the fly
    show=True,            # can show/hide window
    vsync=False,          # can set window to sync to blank
    resizable=True,       # can toggle resizability (e.g., no user resizing)
    decorate=True,        # can toggle decorations
    fullscreen=True,      # fullscreen window support
    context=False,        # can share contexts between windows
    multi_window=True,    # can use multiple windows at once
    scroll=True,          # scroll-wheel events are supported
    parent=True,          # can pass native widget backend parent
    always_on_top=True,   # can be made always-on-top
)


# ------------------------------------------------------- set_configuration ---
def _set_config(c):
    """Set gl configuration for template.
    Currently not used for Tkinter backend.
    """
    return []


# ------------------------------------------------------------- application ---

class _TkInstanceManager:
    _tk_inst = None         # Reference to tk.Tk instance
    _tk_inst_owned = False  # Whether we created the Tk instance or not
    _canvasses = []         # References to created CanvasBackends

    @classmethod
    def get_tk_instance(cls):
        """Return the Tk instance.

        Returns
        -------
        tk.Tk
            The tk.Tk instance.
        """
        if cls._tk_inst is None:
            if tk._default_root:
                # There already is a tk.Tk() instance available
                cls._tk_inst = tk._default_root
                cls._tk_inst_owned = False
            else:
                # Create our own top level Tk instance
                cls._tk_inst = tk.Tk()
                cls._tk_inst.withdraw()
                cls._tk_inst_owned = True
        return cls._tk_inst

    @classmethod
    def get_canvasses(cls):
        """Return a list of CanvasBackends.

        Returns
        -------
        list
            A list with CanvasBackends.
        """
        return cls._canvasses

    @classmethod
    def new_toplevel(cls, canvas, *args, **kwargs):
        """Create and return a new withdrawn Toplevel.
        Create a tk.Toplevel with the given args and kwargs,
        minimize it and add it to the list before returning

        Parameters
        ----------
        canvas : CanvasBackend
            The CanvasBackend instance that wants a new Toplevel.
        *args
            Variable length argument list.
        **kwargs
            Arbitrary keyword arguments.

        Returns
        -------
        tk.Toplevel
            Return the created tk.Toplevel
        """
        tl = tk.Toplevel(cls._tk_inst, *args, **kwargs)
        tl.withdraw()
        cls._canvasses.append(canvas)
        return tl

    @classmethod
    def del_toplevel(cls, canvas=None):
        """
        Destroy the given Toplevel, and if it was the last one,
        also destroy the Tk instance if we created it.

        Parameters
        ----------
        canvas : CanvasBackend
            The CanvasBackend to destroy, defaults to None.
        """
        if canvas:
            try:
                canvas.destroy()
                if canvas.top:
                    canvas.top.destroy()
                cls._canvasses.remove(canvas)
            except Exception:
                pass

        # If there are no Toplevels left, quit the mainloop.
        if cls._tk_inst and not cls._canvasses and cls._tk_inst_owned:
            cls._tk_inst.quit()
            cls._tk_inst.destroy()
            cls._tk_inst = None


class ApplicationBackend(BaseApplicationBackend):
    def _vispy_get_backend_name(self):
        """
        Returns
        -------
        str
            The name of the backend.
        """
        return tk.__name__

    def _vispy_process_events(self):
        """Process events related to the spawned Tk application window.
        First, update the Tk instance, then call `_delayed_update`
        on every created Toplevel (to force a redraw), and process some Tkinter
        GUI events by calling the Tk.mainloop and immediately exiting.
        """
        # Update idle tasks first (probably not required)
        app = self._vispy_get_native_app()
        app.update_idletasks()

        # Update every active Canvas window
        for c in _TkInstanceManager.get_canvasses():
            c._delayed_update()

        # Process some events in the main Tkinter event loop
        # And quit so we can continue elsewhere (call blocks normally)
        app.after(0, lambda: app.quit())
        app.mainloop()

    def _vispy_run(self):
        """Start the Tk.mainloop. This will block until all Tk windows are destroyed."""
        self._vispy_get_native_app().mainloop()

    def _vispy_quit(self):
        """Destroy each created Toplevel by calling _vispy_close on it.
        If there are no Toplevels left, also destroy the Tk instance.
        """
        for c in _TkInstanceManager.get_canvasses():
            c._vispy_close()
        _TkInstanceManager.del_toplevel()

    def _vispy_get_native_app(self):
        """Get or create the Tk instance.

        Returns
        -------
        tk.Tk
            The tk.Tk instance.
        """
        return _TkInstanceManager.get_tk_instance()


# ------------------------------------------------------------------ canvas ---


class CanvasBackend(BaseCanvasBackend, OpenGLFrame):
    """Tkinter backend for Canvas abstract class.
    Uses pyopengltk.OpenGLFrame as the internal tk.Frame instance that
    is able to receive OpenGL draw commands and display the results,
    while also being placeable in another Toplevel window.
    """

    def __init__(self, vispy_canvas, **kwargs):
        BaseCanvasBackend.__init__(self, vispy_canvas)
        p = self._process_backend_kwargs(kwargs)

        self._double_click_supported = True

        # Deal with config
        # ... use context.config
        # Deal with context
        p.context.shared.add_ref('tk', self)
        if p.context.shared.ref is self:
            self._native_context = None
        else:
            self._native_context = p.context.shared.ref._native_context

        # Pop args unrecognised by OpenGLFrame
        kwargs.pop("parent")
        kwargs.pop("title")
        kwargs.pop("size")
        kwargs.pop("position")
        kwargs.pop("show")
        kwargs.pop("vsync")
        kwargs.pop("resizable")
        kwargs.pop("decorate")
        kwargs.pop("always_on_top")
        kwargs.pop("fullscreen")
        kwargs.pop("context")

        if p.parent is None:
            # Create native window and top level
            self.top = _TkInstanceManager.new_toplevel(self)

            # Check input args and call appropriate set-up functions.
            if p.title:
                self._vispy_set_title(p.title)
            if p.size:
                self._vispy_set_size(p.size[0], p.size[1])
            if p.position:
                self._vispy_set_position(p.position[0], p.position[1])

            self.top.update_idletasks()

            if not p.resizable:
                self.top.resizable(False, False)
            if not p.decorate:
                self.top.overrideredirect(True)
            if p.always_on_top:
                self.top.wm_attributes("-topmost", "True")
            self._fullscreen = bool(p.fullscreen)

            self.top.protocol("WM_DELETE_WINDOW", self._vispy_close)
            parent = self.top
        else:
            # Use given parent as top level
            self.top = None
            parent = p.parent
            self._fullscreen = False

        self._init = False
        self.is_destroyed = False
        self._dynamic_keymap = {}

        OpenGLFrame.__init__(self, parent, **kwargs)

        if self.top:
            # Embed canvas in top (new window) if this was created
            self.top.configure(bg="black")
            self.pack(fill=tk.BOTH, expand=True)

            # Also bind the key events to the top window instead.
            self.top.bind("<Any-KeyPress>", self._on_key_down)
            self.top.bind("<Any-KeyRelease>", self._on_key_up)
        else:
            # If no top, bind key events to the canvas itself.
            self.bind("<Any-KeyPress>", self._on_key_down)
            self.bind("<Any-KeyRelease>", self._on_key_up)

        # Bind the other events to our internal methods.
        self.bind("<Enter>", self._on_mouse_enter)  # This also binds MouseWheel
        self.bind("<Leave>", self._on_mouse_leave)  # This also unbinds MouseWheel
        self.bind("<Motion>", self._on_mouse_move)
        self.bind("<Any-Button>", self._on_mouse_button_press)
        self.bind("<Double-Any-Button>", self._on_mouse_double_button_press)
        self.bind("<Any-ButtonRelease>", self._on_mouse_button_release)
        self.bind("<Configure>", self._on_configure, add='+')

        self._vispy_set_visible(p.show)
        self.focus_force()

    def initgl(self):
        """Overridden from OpenGLFrame
        Gets called on init or when the frame is remapped into its container.
        """
        if not hasattr(self, "_native_context") or self._native_context is None:
            # Workaround to get OpenGLFrame.__context for reference here
            # if access would ever be needed from self._native_context.
            # FIXME: Context sharing this way seems unsupported
            self._native_context = vars(self).get("_CanvasBackend__context", None)

        self.update_idletasks()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClearColor(0.0, 0.0, 0.0, 0.0)

    def redraw(self, *args):
        """Overridden from OpenGLFrame
        Gets called when the OpenGLFrame redraws itself.
        It will set the current buffer, call self.redraw() and
        swap buffers afterwards.
        """
        if self._vispy_canvas is None:
            return
        if not self._init:
            self._initialize()
        self._vispy_canvas.set_current()
        self._vispy_canvas.events.draw(region=None)

    def _delayed_update(self):
        """
        Expose a new frame to the canvas. This will call self.redraw() internally.

        The self.animate sets the refresh rate in milliseconds. Using this is not
        necessary because VisPy will use the TimerBackend to periodically call
        self._vispy_update, resulting in the exact same behaviour.
        So we set it to `0` to tell OpenGLFrame not to redraw itself on its own.
        """
        if self.is_destroyed:
            return
        self.animate = 0
        self.tkExpose(None)

    def _on_configure(self, e):
        """Called when the frame get configured or resized."""
        if self._vispy_canvas is None or not self._init:
            return
        size_tup = e if isinstance(e, tuple) else (e.width, e.height)
        self._vispy_canvas.events.resize(size=size_tup)

    def _initialize(self):
        """Initialise the Canvas for drawing."""
        self.initgl()
        if self._vispy_canvas is None:
            return
        self._init = True
        self._vispy_canvas.set_current()
        self._vispy_canvas.events.initialize()
        self.update_idletasks()
        self._on_configure(self._vispy_get_size())

    def _vispy_warmup(self):
        """Provided for VisPy tests, so they can 'warm the canvas up'.
        Mostly taken from the wxWidgets backend.
        """
        tk_inst = _TkInstanceManager.get_tk_instance()

        etime = time() + 0.3
        while time() < etime:
            sleep(0.01)
            self._vispy_canvas.set_current()
            self._vispy_canvas.app.process_events()

            tk_inst.after(0, lambda: tk_inst.quit())
            tk_inst.mainloop()

    def _parse_state(self, e):
        """Helper to parse event.state into modifier keys.

        Parameters
        ----------
        e : tk.Event
            The passed in Event.

        Returns
        -------
        list
            A list of modifier keys that are active (from vispy's keys)
        """
        return [key for mask, key in KEY_STATE_MAP.items() if e.state & mask]

    def _parse_keys(self, e):
        """Helper to parse key states into Vispy keys.

        Parameters
        ----------
        e : tk.Event
            The passed in Event.

        Returns
        -------
        tuple
            A tuple (key.Key(), chr(key)), which has the vispy key object and
            the character representation if available.
        """
        if e.keysym_num in KEYMAP:
            return KEYMAP[e.keysym_num], ""
        # e.char, e.keycode, e.keysym, e.keysym_num
        if e.char:
            self._dynamic_keymap[e.keycode] = e.char
            return keys.Key(e.char), e.char

        if e.keycode in self._dynamic_keymap:
            char = self._dynamic_keymap[e.keycode]
            return keys.Key(char), char

        warnings.warn("The key you typed is not supported by the tkinter backend."
                      "Please map your functionality to a different key")
        return None, None

    def _on_mouse_enter(self, e):
        """Event callback when the mouse enters the canvas.

        Parameters
        ----------
        e : tk.Event
            The passed in Event.
        """
        if self._vispy_canvas is None:
            return
        if _tk_on_linux:
            # On Linux, bind wheel as buttons instead
            self.bind_all("<Button-4>", self._on_mouse_wheel)
            self.bind_all("<Button-5>", self._on_mouse_wheel)
        else:
            # Other platforms, bind wheel event
            # FIXME: What to do on Darwin?
            self.bind_all("<MouseWheel>", self._on_mouse_wheel)

        self._vispy_mouse_move(
            pos=(e.x, e.y), modifiers=self._parse_state(e))

    def _on_mouse_leave(self, e):
        """Event callback when the mouse leaves the canvas.

        Parameters
        ----------
        e : tk.Event
            The passed in Event.
        """
        if self._vispy_canvas is None:
            return
        # Unbind mouse wheel events when not over the canvas any more.
        if _tk_on_linux:
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")
        else:
            self.unbind_all("<MouseWheel>")

    def _on_mouse_move(self, e):
        """Event callback when the mouse is moved within the canvas.

        Parameters
        ----------
        e : tk.Event
            The passed in Event.
        """
        if self._vispy_canvas is None:
            return
        self._vispy_mouse_move(
            pos=(e.x, e.y), modifiers=self._parse_state(e))

    def _on_mouse_wheel(self, e):
        """Event callback when the mouse wheel changes within the canvas.

        Parameters
        ----------
        e : tk.Event
            The passed in Event.
        """
        if self._vispy_canvas is None:
            return
        if _tk_on_linux:
            # Fix mouse wheel delta
            e.delta = {4: 120, 5: -120}.get(e.num, 0)
        self._vispy_canvas.events.mouse_wheel(
            delta=(0.0, float(e.delta / 120)),
            pos=(e.x, e.y), modifiers=self._parse_state(e))

    def _on_mouse_button_press(self, e):
        """Event callback when a mouse button is pressed within the canvas.

        Parameters
        ----------
        e : tk.Event
            The passed in Event.
        """
        if self._vispy_canvas is None:
            return
        # Ignore MouseWheel on linux
        if _tk_on_linux and e.num in (4, 5):
            return
        self._vispy_mouse_press(
            pos=(e.x, e.y), button=MOUSE_BUTTON_MAP.get(e.num, e.num), modifiers=self._parse_state(e))

    def _vispy_detect_double_click(self, e):
        """Override base class function
        since double click handling is native in Tk.
        """
        pass

    def _on_mouse_double_button_press(self, e):
        """Event callback when a mouse button is double clicked within the canvas.

        Parameters
        ----------
        e : tk.Event
            The passed in Event.
        """
        if self._vispy_canvas is None:
            return
        # Ignore MouseWheel on linux
        if _tk_on_linux and e.num in (4, 5):
            return
        self._vispy_mouse_double_click(
            pos=(e.x, e.y), button=MOUSE_BUTTON_MAP.get(e.num, e.num), modifiers=self._parse_state(e))

    def _on_mouse_button_release(self, e):
        """Event callback when a mouse button is released within the canvas.

        Parameters
        ----------
        e : tk.Event
            The passed in Event.
        """
        if self._vispy_canvas is None:
            return
        # Ignore MouseWheel on linux
        if _tk_on_linux and e.num in (4, 5):
            return
        self._vispy_mouse_release(
            pos=(e.x, e.y), button=MOUSE_BUTTON_MAP.get(e.num, e.num), modifiers=self._parse_state(e))

    def _on_key_down(self, e):
        """Event callback when a key is pressed within the canvas or window.

        Ignore keys.ESCAPE if this is an embedded canvas,
        as this would make it unresponsive (because it won't close the entire window),
        while still being updateable.

        Parameters
        ----------
        e : tk.Event
            The passed in Event.
        """
        if self._vispy_canvas is None:
            return
        key, text = self._parse_keys(e)
        if not self.top and key == keys.ESCAPE:
            return
        self._vispy_canvas.events.key_press(
            key=key, text=text, modifiers=self._parse_state(e))

    def _on_key_up(self, e):
        """Event callback when a key is released within the canvas or window.

        Ignore keys.ESCAPE if this is an embedded canvas,
        as this would make it unresponsive (because it won't close the entire window),
        while still being updateable.

        Parameters
        ----------
        e : tk.Event
            The passed in Event.
        """
        if self._vispy_canvas is None:
            return
        key, text = self._parse_keys(e)
        if not self.top and key == keys.ESCAPE:
            return
        self._vispy_canvas.events.key_release(
            key=key, text=text, modifiers=self._parse_state(e))

    def _vispy_set_current(self):
        """Make this the current context."""
        if not self.is_destroyed:
            self.tkMakeCurrent()

    def _vispy_swap_buffers(self):
        """Swap front and back buffer. This is done internally inside OpenGLFrame."""
        self._vispy_canvas.set_current()

    def _vispy_set_title(self, title):
        """Set the window title. Has no effect for widgets."""
        if self.top:
            self.top.title(title)

    def _vispy_set_size(self, w, h):
        """Set size of the window. Has no effect for widgets."""
        if self.top:
            self.top.geometry(f"{w}x{h}")

    def _vispy_set_position(self, x, y):
        """Set location of the window. Has no effect for widgets."""
        if self.top:
            self.top.geometry(f"+{x}+{y}")

    def _vispy_set_visible(self, visible):
        """Show or hide the window. Has no effect for widgets."""
        if self.top:
            if visible:
                self.top.wm_deiconify()
                self.top.lift()
                self.top.attributes('-fullscreen', self._fullscreen)
            else:
                self.top.withdraw()

    def _vispy_set_fullscreen(self, fullscreen):
        """Set the current fullscreen state.

        Has no effect for widgets. If you want it to become fullscreen,
        while embedded in another Toplevel window, you should make that
        window fullscreen instead.
        """
        self._fullscreen = bool(fullscreen)
        if self.top:
            self._vispy_set_visible(True)

    def _vispy_update(self):
        """Invoke a redraw

        Delay this by letting Tk call it later, even a delay of 0 will do.
        Doing this, prevents EventEmitter loops that are caused
        by wanting to draw too fast.
        """
        self.after(0, self._delayed_update)

    def _vispy_close(self):
        """Force the window to close, destroying the canvas in the process.

        When this was the last VisPy window, also quit the Tk instance.
        This will not interfere if there is already another user window,
        unrelated top VisPy open.
        """
        if self.top and not self.is_destroyed:
            self.is_destroyed = True
            self._vispy_canvas.close()
            _TkInstanceManager.del_toplevel(self)

    def destroy(self):
        """Callback when the window gets closed.
        Destroy the VisPy canvas by calling close on it.
        """
        self._vispy_canvas.close()

    def _vispy_get_size(self):
        """Return the actual size of the frame."""
        if self.top:
            self.top.update_idletasks()
        return self.winfo_width(), self.winfo_height()

    def _vispy_get_position(self):
        """Return the widget or window position."""
        return self.winfo_x(), self.winfo_y()

    def _vispy_get_fullscreen(self):
        """Return the last set full screen state, regardless if it's actually in that state.

        When using the canvas as a widget, it will not go into fullscreen.
        See _vispy_set_fullscreen
        """
        return self._fullscreen


# ------------------------------------------------------------------- timer ---

class TimerBackend(BaseTimerBackend):
    def __init__(self, vispy_timer):
        BaseTimerBackend.__init__(self, vispy_timer)
        self._tk = _TkInstanceManager.get_tk_instance()
        if self._tk is None:
            raise Exception("TimerBackend: No toplevel?")
        self._id = None
        self.last_interval = 1

    def _vispy_start(self, interval):
        """Start the timer.
        Use Tk.after to schedule timer events.
        """
        self._vispy_stop()
        self.last_interval = max(0, int(round(interval * 1000)))
        self._id = self._tk.after(self.last_interval, self._vispy_timeout)

    def _vispy_stop(self):
        """Stop the timer.
        Unschedule the previous callback if it exists.
        """
        if self._id is not None:
            self._tk.after_cancel(self._id)
            self._id = None

    def _vispy_timeout(self):
        """Callback when the timer finishes.
        Also reschedules the next callback.
        """
        self._vispy_timer._timeout()
        self._id = self._tk.after(self.last_interval, self._vispy_timeout)
