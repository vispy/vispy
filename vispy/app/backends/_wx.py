# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
vispy backend for wxPython.
"""

from __future__ import division

from time import sleep

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend, BaseSharedContext)
from ...util import keys
from ...util.ptime import time


# -------------------------------------------------------------------- init ---

try:
    import wx
    from wx.glcanvas import GLCanvas, GLContext

    # Map native keys to vispy keys
    KEYMAP = {
        wx.WXK_SHIFT: keys.SHIFT,
        wx.WXK_CONTROL: keys.CONTROL,
        wx.WXK_ALT: keys.ALT,

        wx.WXK_LEFT: keys.LEFT,
        wx.WXK_UP: keys.UP,
        wx.WXK_RIGHT: keys.RIGHT,
        wx.WXK_DOWN: keys.DOWN,
        wx.WXK_PAGEUP: keys.PAGEUP,
        wx.WXK_PAGEDOWN: keys.PAGEDOWN,

        wx.WXK_INSERT: keys.INSERT,
        wx.WXK_DELETE: keys.DELETE,
        wx.WXK_HOME: keys.HOME,
        wx.WXK_END: keys.END,

        wx.WXK_ESCAPE: keys.ESCAPE,
        wx.WXK_BACK: keys.BACKSPACE,

        wx.WXK_F1: keys.F1,
        wx.WXK_F2: keys.F2,
        wx.WXK_F3: keys.F3,
        wx.WXK_F4: keys.F4,
        wx.WXK_F5: keys.F5,
        wx.WXK_F6: keys.F6,
        wx.WXK_F7: keys.F7,
        wx.WXK_F8: keys.F8,
        wx.WXK_F9: keys.F9,
        wx.WXK_F10: keys.F10,
        wx.WXK_F11: keys.F11,
        wx.WXK_F12: keys.F12,

        wx.WXK_SPACE: keys.SPACE,
        wx.WXK_RETURN: keys.ENTER,  # == pyglet.window.key.RETURN
        wx.WXK_NUMPAD_ENTER: keys.ENTER,
        wx.WXK_TAB: keys.TAB,
    }
except Exception as exp:
    available, testable, why_not, which = False, False, str(exp), None

    class GLCanvas(object):
        pass
else:
    available, testable, why_not = True, True, None
    which = 'wxPython ' + str(wx.__version__)


# -------------------------------------------------------------- capability ---

capability = dict(  # things that can be set by the backend
    title=True,
    size=True,
    position=True,
    show=True,
    vsync=True,
    resizable=False,
    decorate=True,
    fullscreen=False,
    context=True,
    multi_window=True,
    scroll=False,
    parent=True,
)


# ------------------------------------------------------- set_configuration ---

def _set_config(config):
    """Set gl configuration"""
    raise NotImplementedError
    # config['red_size']
    # config['green_size']
    # config['blue_size']
    # config['alpha_size']

    # config['depth_size']
    # config['stencil_size']
    # config['double_buffer']
    # config['stereo']
    # config['samples']
    # return pyglet_config


class SharedContext(BaseSharedContext):
    _backend = 'pyglet'


# ------------------------------------------------------------- application ---

_wx_app = None


class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)

    def _vispy_get_backend_name(self):
        return 'wx'

    def _vispy_process_events(self):
        # pyglet.app.platform_event_loop.step(0.0)
        _wx_app.ProcessPendingEvents()

    def _vispy_run(self):
        return _wx_app.MainLoop()

    def _vispy_quit(self):
        global _wx_app
        _wx_app.Destroy()
        _wx_app = None

    def _vispy_get_native_app(self):
        # Get native app in save way. Taken from guisupport.py
        global _wx_app
        _wx_app = wx.App() if _wx_app is None else _wx_app
        return _wx_app


# ------------------------------------------------------------------ canvas ---

def _get_mods(evt):
    """Helper to extract list of mods from event"""
    mods = []
    mods += [keys.CONTROL] if evt.ControlDown() else []
    mods += [keys.ALT] if evt.AltDown() else []
    mods += [keys.SHIFT] if evt.ShiftDown() else []
    mods += [keys.META] if evt.MetaDown() else []
    return mods


def _process_key(evt):
    """Helper to convert from wx keycode to vispy keycode"""
    key = evt.GetKeyCode()
    if key in KEYMAP:
        return KEYMAP[key]
    if 97 <= key <= 122:
        key -= 32
    if key >= 32 and key <= 127:
        return keys.Key(chr(key))
    else:
        return None


class CanvasBackend(GLCanvas, BaseCanvasBackend):

    """ wxPython backend for Canvas abstract class."""

    def __init__(self, **kwargs):
        BaseCanvasBackend.__init__(self, capability, SharedContext)
        title, size, position, show, vsync, resize, dec, fs, parent, context, \
            vispy_canvas = self._process_backend_kwargs(kwargs)
        self._vispy_canvas = vispy_canvas
        if not isinstance(context, (dict, SharedContext)):
            raise TypeError('context must be a dict or wx SharedContext')
        style = wx.NO_BORDER if not dec else 0
        GLCanvas.__init__(self, parent, -1, position, size, style, title)
        self.SetDoubleBuffered(vsync)
        self._vispy_set_title(title)
        if not isinstance(context, SharedContext):
            # config = _set_config(context)  # XXX FIX THIS
            self._context = GLContext(self)
        else:
            self._context = context.value
        if position is not None:
            self._vispy_set_position(*position)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse_event)  # all mouse events
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)

    def on_resize(self, event):
        size = self._vispy_get_size()
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.resize(size=size)

    def on_paint(self, event):
        if self._vispy_canvas is None:
            return
        dc = wx.PaintDC(self)  # needed for wx
        if not self._init:
            self._initialize()
        self._vispy_set_current()
        self._vispy_canvas.events.draw(region=None)
        del dc

    def _initialize(self):
        if self._vispy_canvas is None:
            return
        self._init = True
        self._vispy_set_current()
        self._vispy_canvas.events.initialize()

    def _vispy_set_current(self):
        self.SetCurrent(self._context)

    @property
    def _vispy_context(self):
        """Context to return for sharing"""
        return SharedContext(self._context)

    def _vispy_warmup(self):
        etime = time() + 0.4  # XXX CHECK ME
        while time() < etime:
            sleep(0.01)
            self._vispy_set_current()
            self._vispy_canvas.app.process_events()

    def _vispy_swap_buffers(self):
        # Swap front and back buffer
        self.SwapBuffers()

    def _vispy_set_title(self, title):
        # Set the window title. Has no effect for widgets
        self.SetLabel(title)

    def _vispy_set_size(self, w, h):
        # Set size of the widget or window
        self.SetSize((w, h))

    def _vispy_set_position(self, x, y):
        # Set positionof the widget or window. May have no effect for widgets
        self.SetPosition((x, y))

    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        self.Show(visible)

    def _vispy_update(self):
        # Invoke a redraw
        self.Refresh()

    def _vispy_close(self):
        # Force the window or widget to shut down
        self.Close()

    def _vispy_get_size(self):
        w, h = self.GetClientSize()
        return w, h

    def _vispy_get_position(self):
        x, y = self.GetPosition()
        return x, y

    def on_close(self):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.close()

    def on_mouse_event(self, evt):
        if self._vispy_canvas is None:
            return
        pos = (evt.GetX(), evt.GetY())
        mods = _get_mods(evt)
        if evt.GetWheelRotation != 0:
            delta = (0., float(evt.GetWheelRotation()))
            self._vispy_canvas.events.mouse_wheel(delta=delta, pos=pos,
                                                  modifiers=mods)
        elif evt.Moving() or evt.Dragging():  # mouse move event
            self._vispy_mouse_move(pos=pos, modifiers=mods)
        elif evt.ButtonDown():
            if evt.LeftDown():
                button = 0
            elif evt.MiddleDown():
                button = 1
            elif evt.RightDown():
                button = 2
            else:
                return
            self._vispy_mouse_press(pos=pos, button=button, modifiers=mods)
        elif evt.ButtonUp():
            if evt.LeftUp():
                button = 0
            elif evt.MiddleUp():
                button = 1
            elif evt.RightUp():
                button = 2
            else:
                return
            self._vispy_mouse_release(pos=pos, button=button, modifiers=mods)

    def on_key_down(self, evt):
        self._vispy_canvas.events.key_press(key=_process_key(evt), text='',
                                            modifiers=_get_mods(evt))

    def on_key_up(self, evt):
        self._vispy_canvas.events.key_release(key=_process_key(evt), text='',
                                              modifiers=_get_mods(evt))


# ------------------------------------------------------------------- timer ---

class TimerBackend(BaseTimerBackend):

    def __init__(self, vispy_timer):
        BaseTimerBackend.__init__(self, vispy_timer)
        self._timer = wx.Timer(None, -1)

    def _vispy_start(self, interval):
        self._timer.Start(interval / 1000., False)

    def _vispy_stop(self):
        self._timer.Stop()
