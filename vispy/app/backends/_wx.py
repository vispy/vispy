# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""vispy backend for wxPython."""

from __future__ import division

from time import sleep
import gc
import warnings

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend)
from ...util import keys, logger
from ...util.ptime import time
from ... import config

USE_EGL = config['gl_backend'].lower().startswith('es')


# -------------------------------------------------------------------- init ---

try:
    # avoid silly locale warning on OSX
    with warnings.catch_warnings(record=True):
        import wx
        from wx import glcanvas
        from wx.glcanvas import GLCanvas

    # Map native keys to vispy keys
    KEYMAP = {
        wx.WXK_SHIFT: keys.SHIFT,
        wx.WXK_CONTROL: keys.CONTROL,
        wx.WXK_ALT: keys.ALT,
        wx.WXK_WINDOWS_MENU: keys.META,

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
    if USE_EGL:
        available, testable, why_not = False, False, 'EGL not supported'
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
    resizable=True,
    decorate=True,
    fullscreen=True,
    context=True,
    multi_window=True,
    scroll=True,
    parent=True,
    always_on_top=True,
)


# ------------------------------------------------------- set_configuration ---

def _set_config(c):
    """Set gl configuration"""
    gl_attribs = [glcanvas.WX_GL_RGBA,
                  glcanvas.WX_GL_DEPTH_SIZE, c['depth_size'],
                  glcanvas.WX_GL_STENCIL_SIZE, c['stencil_size'],
                  glcanvas.WX_GL_MIN_RED, c['red_size'],
                  glcanvas.WX_GL_MIN_GREEN, c['green_size'],
                  glcanvas.WX_GL_MIN_BLUE, c['blue_size'],
                  glcanvas.WX_GL_MIN_ALPHA, c['alpha_size']]
    gl_attribs += [glcanvas.WX_GL_DOUBLEBUFFER] if c['double_buffer'] else []
    gl_attribs += [glcanvas.WX_GL_STEREO] if c['stereo'] else []
    return gl_attribs


# ------------------------------------------------------------- application ---

_wx_app = None
_timers = []


class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)
        self._event_loop = wx.GUIEventLoop()
        wx.EventLoop.SetActive(self._event_loop)

    def _vispy_get_backend_name(self):
        return 'wx'

    def _vispy_process_events(self):
        # inpsired by https://github.com/wxWidgets/wxPython/blob/master/
        #             samples/mainloop/mainloop.py
        for _ in range(3):  # trial-and-error found this to work (!)
            while self._event_loop.Pending():
                self._event_loop.Dispatch()
            if hasattr(_wx_app, 'ProcessIdle'):
                _wx_app.ProcessIdle()
            else:
                self._event_loop.ProcessIdle()
            sleep(0.01)

    def _vispy_run(self):
        return _wx_app.MainLoop()

    def _vispy_quit(self):
        global _wx_app
        _wx_app.ExitMainLoop()

    def _vispy_get_native_app(self):
        # Get native app in save way. Taken from guisupport.py
        global _wx_app
        _wx_app = wx.GetApp()  # in case the user already has one
        if _wx_app is None:
            if hasattr(wx, 'App'):
                _wx_app = wx.App()
            else:
                # legacy wx
                _wx_app = wx.PySimpleApp()
        _wx_app.SetExitOnFrameDelete(True)
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
        return KEYMAP[key], ''
    if 97 <= key <= 122:
        key -= 32
    if key >= 32 and key <= 127:
        return keys.Key(chr(key)), chr(key)
    else:
        return None, None


class DummySize(object):
    def __init__(self, size):
        self.size = size

    def GetSize(self):
        return self.size

    def Skip(self):
        pass


class CanvasBackend(GLCanvas, BaseCanvasBackend):
    """wxPython backend for Canvas abstract class."""

    def __init__(self, vispy_canvas, **kwargs):
        BaseCanvasBackend.__init__(self, vispy_canvas)
        p = self._process_backend_kwargs(kwargs)

        # WX supports OS double-click events, so we set this here to
        # avoid double events
        self._double_click_supported = True

        # Set config
        self._gl_attribs = _set_config(p.context.config)
        # Deal with context
        p.context.shared.add_ref('wx', self)
        if p.context.shared.ref is self:
            self._gl_context = None  # set for real once we init the GLCanvas
        else:
            self._gl_context = p.context.shared.ref._gl_context

        if p.position is None:
            pos = wx.DefaultPosition
        else:
            pos = p.position

        if p.parent is None:
            style = (wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.CLOSE_BOX |
                     wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN)
            style |= wx.NO_BORDER if not p.decorate else wx.RESIZE_BORDER
            style |= wx.STAY_ON_TOP if p.always_on_top else 0
            self._frame = wx.Frame(None, wx.ID_ANY, p.title, pos, p.size,
                                   style)

            if not p.resizable:
                self._frame.SetSizeHints(p.size[0], p.size[1],
                                         p.size[0], p.size[1])
            if p.fullscreen is not False:
                if p.fullscreen is not True:
                    logger.warning('Cannot specify monitor number for wx '
                                   'fullscreen, using default')
                self._fullscreen = True
            else:
                self._fullscreen = False
            _wx_app.SetTopWindow(self._frame)
            parent = self._frame
            self._frame.Show()
            self._frame.Raise()
            self._frame.Bind(wx.EVT_CLOSE, self.on_close)
        else:
            parent = p.parent
            self._frame = None
            self._fullscreen = False
        self._init = False
        GLCanvas.__init__(self, parent, wx.ID_ANY, pos=pos,
                          size=p.size, style=0, name='GLCanvas',
                          attribList=self._gl_attribs)

        if self._gl_context is None:
            self._gl_context = glcanvas.GLContext(self)

        self.SetFocus()
        self._vispy_set_title(p.title)
        self._size = None
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_PAINT, self.on_draw)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse_event)
        self._size_init = p.size
        self._vispy_set_visible(p.show)

    def on_resize(self, event):
        if self._vispy_canvas is None or not self._init:
            event.Skip()
            return
        size = event.GetSize()
        self._vispy_canvas.events.resize(size=size)
        self.Refresh()
        event.Skip()

    def on_draw(self, event):
        if self._vispy_canvas is None:
            return
        dc = wx.PaintDC(self)  # needed for wx
        if not self._init:
            self._initialize()
        self._vispy_canvas.set_current()
        self._vispy_canvas.events.draw(region=None)
        del dc
        event.Skip()

    def _initialize(self):
        if self._vispy_canvas is None:
            return
        self._init = True
        self._vispy_canvas.set_current()
        self._vispy_canvas.events.initialize()
        self.on_resize(DummySize(self._size_init))

    def _vispy_set_current(self):
        if self.IsShown():
            self.SetCurrent(self._gl_context)

    def _vispy_warmup(self):
        etime = time() + 0.3
        while time() < etime:
            sleep(0.01)
            self._vispy_canvas.set_current()
            self._vispy_canvas.app.process_events()

    def _vispy_swap_buffers(self):
        # Swap front and back buffer
        self._vispy_canvas.set_current()
        self.SwapBuffers()

    def _vispy_set_title(self, title):
        # Set the window title. Has no effect for widgets
        if self._frame is not None:
            self._frame.SetLabel(title)

    def _vispy_set_size(self, w, h):
        # Set size of the widget or window
        if not self._init:
            self._size_init = (w, h)
        if hasattr(self, 'SetSize'):
            # phoenix
            self.SetSize(w, h)
        else:
            # legacy
            self.SetSizeWH(w, h)

    def _vispy_set_position(self, x, y):
        # Set positionof the widget or window. May have no effect for widgets
        if self._frame is not None:
            self._frame.SetPosition((x, y))

    def _vispy_get_fullscreen(self):
        return self._fullscreen

    def _vispy_set_fullscreen(self, fullscreen):
        if self._frame is not None:
            self._fullscreen = bool(fullscreen)
            self._vispy_set_visible(True)

    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        self.Show(visible)
        if visible:
            if self._frame is not None:
                self._frame.ShowFullScreen(self._fullscreen)

    def _vispy_update(self):
        # Invoke a redraw
        self.Refresh()

    def _vispy_close(self):
        if self._vispy_canvas is None:
            return
        # Force the window or widget to shut down
        canvas = self
        frame = self._frame
        self._gl_context = None  # let RC destroy this in case it's shared
        canvas.Close()
        canvas.Destroy()
        if frame:
            frame.Close()
            frame.Destroy()
        gc.collect()  # ensure context gets destroyed if it should be

    def _vispy_get_size(self):
        if self._vispy_canvas is None:
            return
        w, h = self.GetClientSize()
        return w, h

    def _vispy_get_physical_size(self):
        w, h = self.GetClientSize()
        ratio = self.GetContentScaleFactor()
        return int(w * ratio), int(h * ratio)

    def _vispy_get_position(self):
        if self._vispy_canvas is None:
            return
        x, y = self.GetPosition()
        return x, y

    def on_close(self, evt):
        if not self:  # wx control evaluates to false if C++ part deleted
            return
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.close()

    def on_mouse_event(self, evt):
        if self._vispy_canvas is None:
            return
        pos = (evt.GetX(), evt.GetY())
        mods = _get_mods(evt)
        if evt.GetWheelRotation() != 0:
            delta = (0., float(evt.GetWheelRotation())/120.0)
            self._vispy_canvas.events.mouse_wheel(delta=delta, pos=pos,
                                                  modifiers=mods)
        elif evt.Moving() or evt.Dragging():  # mouse move event
            self._vispy_mouse_move(pos=pos, modifiers=mods)
        elif evt.ButtonDown():
            if evt.LeftDown():
                button = 1
            elif evt.MiddleDown():
                button = 3
            elif evt.RightDown():
                button = 2
            else:
                evt.Skip()
            self._vispy_mouse_press(pos=pos, button=button, modifiers=mods)
        elif evt.ButtonUp():
            if evt.LeftUp():
                button = 1
            elif evt.MiddleUp():
                button = 3
            elif evt.RightUp():
                button = 2
            else:
                evt.Skip()
            self._vispy_mouse_release(pos=pos, button=button, modifiers=mods)
        elif evt.ButtonDClick():
            if evt.LeftDClick():
                button = 1
            elif evt.MiddleDClick():
                button = 3
            elif evt.RightDClick():
                button = 2
            else:
                evt.Skip()
            self._vispy_mouse_press(pos=pos, button=button, modifiers=mods)
            self._vispy_mouse_double_click(pos=pos, button=button,
                                           modifiers=mods)
        evt.Skip()

    def on_key_down(self, evt):
        if self._vispy_canvas is None:
            return
        key, text = _process_key(evt)
        self._vispy_canvas.events.key_press(key=key, text=text,
                                            modifiers=_get_mods(evt))

    def on_key_up(self, evt):
        if self._vispy_canvas is None:
            return
        key, text = _process_key(evt)
        self._vispy_canvas.events.key_release(key=key, text=text,
                                              modifiers=_get_mods(evt))


# ------------------------------------------------------------------- timer ---

class TimerBackend(BaseTimerBackend):

    def __init__(self, vispy_timer):
        BaseTimerBackend.__init__(self, vispy_timer)
        assert _wx_app is not None
        parent = _wx_app.GetTopWindow()  # assume it's the parent window
        self._timer = wx.Timer(parent, -1)
        parent.Bind(wx.EVT_TIMER, self._vispy_timeout, self._timer)

    def _vispy_start(self, interval):
        self._timer.Start(int(interval * 1000.), False)

    def _vispy_stop(self):
        self._timer.Stop()

    def _vispy_timeout(self, evt):
        self._vispy_timer._timeout()
        evt.Skip()
