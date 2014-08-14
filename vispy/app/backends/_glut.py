# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
vispy backend for glut.
"""

from __future__ import division

import sys
from time import sleep, time

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend, BaseSharedContext)
from ...util import ptime, keys, logger

# -------------------------------------------------------------------- init ---

try:
    import OpenGL.error
    import OpenGL.GLUT as glut

    # glut.GLUT_ACTIVE_SHIFT: keys.SHIFT,
    # glut.GLUT_ACTIVE_CTRL: keys.CONTROL,
    # glut.GLUT_ACTIVE_ALT: keys.ALT,
    # -1: keys.META,

    # Map native keys to vispy keys
    KEYMAP = {
        -1: keys.SHIFT,
        -2: keys.CONTROL,
        -3: keys.ALT,
        -4: keys.META,

        glut.GLUT_KEY_LEFT: keys.LEFT,
        glut.GLUT_KEY_UP: keys.UP,
        glut.GLUT_KEY_RIGHT: keys.RIGHT,
        glut.GLUT_KEY_DOWN: keys.DOWN,
        glut.GLUT_KEY_PAGE_UP: keys.PAGEUP,
        glut.GLUT_KEY_PAGE_DOWN: keys.PAGEDOWN,

        glut.GLUT_KEY_INSERT: keys.INSERT,
        chr(127): keys.DELETE,
        glut.GLUT_KEY_HOME: keys.HOME,
        glut.GLUT_KEY_END: keys.END,

        chr(27): keys.ESCAPE,
        chr(8): keys.BACKSPACE,

        glut.GLUT_KEY_F1: keys.F1,
        glut.GLUT_KEY_F2: keys.F2,
        glut.GLUT_KEY_F3: keys.F3,
        glut.GLUT_KEY_F4: keys.F4,
        glut.GLUT_KEY_F5: keys.F5,
        glut.GLUT_KEY_F6: keys.F6,
        glut.GLUT_KEY_F7: keys.F7,
        glut.GLUT_KEY_F8: keys.F8,
        glut.GLUT_KEY_F9: keys.F9,
        glut.GLUT_KEY_F10: keys.F10,
        glut.GLUT_KEY_F11: keys.F11,
        glut.GLUT_KEY_F12: keys.F12,

        ' ': keys.SPACE,
        '\r': keys.ENTER,
        '\n': keys.ENTER,
        '\t': keys.TAB,
    }

    BUTTONMAP = {glut.GLUT_LEFT_BUTTON: 1,
                 glut.GLUT_RIGHT_BUTTON: 2,
                 glut.GLUT_MIDDLE_BUTTON: 3
                 }

    def _get_glut_process_func():
        if hasattr(glut, 'glutMainLoopEvent') and bool(glut.glutMainLoopEvent):
            func = glut.glutMainLoopEvent
        elif hasattr(glut, 'glutCheckLoop') and bool(glut.glutCheckLoop):
            func = glut.glutCheckLoop  # Darwin
        else:
            msg = ('Your implementation of GLUT does not allow '
                   'interactivity. Consider installing freeglut.')
            raise RuntimeError(msg)
        return func
except Exception as exp:
    available, testable, why_not, which = False, False, str(exp), None
else:
    available, why_not, testable = True, None, True
    try:
        _get_glut_process_func()
    except RuntimeError:
        testable, why_not = False, 'No process_func'
    which = 'from OpenGL %s' % OpenGL.__version__


_GLUT_INITIALIZED = False
_VP_GLUT_ALL_WINDOWS = []

# -------------------------------------------------------------- capability ---

capability = dict(  # things that can be set by the backend
    title=True,
    size=True,
    position=True,
    show=True,
    vsync=False,
    resizable=False,
    decorate=False,
    fullscreen=True,
    context=False,
    multi_window=False,
    scroll=False,
    parent=False,
)


# ------------------------------------------------------- set_configuration ---

def _set_config(config):
    """Set gl configuration"""
    s = ""
    st = '~' if sys.platform == 'darwin' else '='
    ge = '>=' if sys.platform == 'darwin' else '='
    s += "red%s%d " % (ge, config['red_size'])
    s += "green%s%d " % (ge, config['green_size'])
    s += "blue%s%d " % (ge, config['blue_size'])
    s += "alpha%s%d " % (ge, config['alpha_size'])
    s += "depth%s%d " % (ge, config['depth_size'])
    s += "stencil%s%d " % (st, config['stencil_size'])
    s += "samples%s%d " % (st, config['samples']) if config['samples'] else ""
    s += "acca=0 " if sys.platform == 'darwin' else ""
    if sys.platform == 'darwin':
        s += "double=1 " if config['double_buffer'] else "single=1 "
        s += "stereo=%d " % config['stereo']
    else:  # freeglut
        s += "double " if config['double_buffer'] else "single "
        s += "stereo " if config['stereo'] else ""
    glut.glutInitDisplayString(s.encode('ASCII'))


class SharedContext(BaseSharedContext):
    _backend = 'glut'


# ------------------------------------------------------------- application ---

class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)
        self._timers = []

    def _add_timer(self, timer):
        if timer not in self._timers:
            self._timers.append(timer)

    def _vispy_get_backend_name(self):
        return 'Glut'

    def _vispy_process_events(self):
        # Determine what function to use, if any
        try:
            func = _get_glut_process_func()
        except RuntimeError:
            self._vispy_process_events = lambda: None
            raise
        # Set for future use, and call!
        self._proc_fun = func
        self._vispy_process_events = self._process_events_and_timer
        self._process_events_and_timer()

    def _process_events_and_timer(self):
        # helper to both call glutMainLoopEvent and tick the timers
        self._proc_fun()
        for timer in self._timers:
            timer._idle_callback()

    def _vispy_run(self):
        self._vispy_get_native_app()  # Force exist
        return glut.glutMainLoop()

    def _vispy_quit(self):
        for timer in self._timers:
            timer._vispy_stop()
        self._timers = []
        if hasattr(glut, 'glutLeaveMainLoop') and bool(glut.glutLeaveMainLoop):
            glut.glutLeaveMainLoop()
        else:
            for win in _VP_GLUT_ALL_WINDOWS:
                win._vispy_close()

    def _vispy_get_native_app(self):
        global _GLUT_INITIALIZED
        if not _GLUT_INITIALIZED:
            glut.glutInit(['vispy'.encode('ASCII')])
            # Prevent exit when closing window
            try:
                glut.glutSetOption(glut.GLUT_ACTION_ON_WINDOW_CLOSE,
                                   glut.GLUT_ACTION_CONTINUE_EXECUTION)
            except Exception:
                pass
            _GLUT_INITIALIZED = True
        return glut


def _set_close_fun(id_, fun):
    # Set close function. See issue #10. For some reason, the function
    # can still not exist even if we checked its boolean status.
    glut.glutSetWindow(id_)
    closeFuncSet = False
    if bool(glut.glutWMCloseFunc):  # OSX specific test
        try:
            glut.glutWMCloseFunc(fun)
            closeFuncSet = True
        except OpenGL.error.NullFunctionError:
            pass
    if not closeFuncSet:
        try:
            glut.glutCloseFunc(fun)
            closeFuncSet = True
        except OpenGL.error.NullFunctionError:
            pass


# ------------------------------------------------------------------ canvas ---

class CanvasBackend(BaseCanvasBackend):

    """ GLUT backend for Canvas abstract class."""

    def __init__(self, **kwargs):
        BaseCanvasBackend.__init__(self, capability, SharedContext)
        title, size, position, show, vsync, resize, dec, fs, parent, context, \
            vispy_canvas = self._process_backend_kwargs(kwargs)
        _set_config(context)
        glut.glutInitWindowSize(size[0], size[1])
        self._id = glut.glutCreateWindow(title.encode('ASCII'))
        if not self._id:
            raise RuntimeError('could not create window')
        glut.glutSetWindow(self._id)
        _VP_GLUT_ALL_WINDOWS.append(self)
        if fs is not False:
            self._fullscreen = True
            self._old_size = size
            if fs is not True:
                logger.warning('Cannot specify monitor for glut fullscreen, '
                               'using default')
            glut.glutFullScreen()
        else:
            self._fullscreen = False

        # Cache of modifiers so we can send modifiers along with mouse motion
        self._modifiers_cache = ()
        self._closed = False  # Keep track whether the widget is closed

        # Register callbacks
        glut.glutDisplayFunc(self.on_draw)
        glut.glutReshapeFunc(self.on_resize)
        # glut.glutVisibilityFunc(self.on_show)
        glut.glutKeyboardFunc(self.on_key_press)
        glut.glutSpecialFunc(self.on_key_press)
        glut.glutKeyboardUpFunc(self.on_key_release)
        glut.glutMouseFunc(self.on_mouse_action)
        glut.glutMotionFunc(self.on_mouse_motion)
        glut.glutPassiveMotionFunc(self.on_mouse_motion)
        _set_close_fun(self._id, self.on_close)
        if position is not None:
            self._vispy_set_position(*position)
        if not show:
            glut.glutHideWindow()
        self._initialized = False
        self._vispy_canvas = vispy_canvas

    @property
    def _vispy_context(self):
        """Context to return for sharing"""
        return SharedContext(None)  # cannot share in GLUT

    def _vispy_warmup(self):
        etime = time() + 0.4  # empirically determined :(
        while time() < etime:
            sleep(0.01)
            self._vispy_set_current()
            self._vispy_canvas.app.process_events()

    @property
    def _vispy_canvas(self):
        """ The parent canvas/window """
        return self._vispy_canvas_

    @_vispy_canvas.setter
    def _vispy_canvas(self, vc):
        # Init events when the property is set by Canvas
        self._vispy_canvas_ = vc
        if vc is not None and not self._initialized:
            self._initialized = True
            self._vispy_set_current()
            self._vispy_canvas.events.initialize()

    def _vispy_set_current(self):
        # Make this the current context
        glut.glutSetWindow(self._id)

    def _vispy_swap_buffers(self):
        # Swap front and back buffer
        glut.glutSetWindow(self._id)
        glut.glutSwapBuffers()

    def _vispy_set_title(self, title):
        # Set the window title. Has no effect for widgets
        glut.glutSetWindow(self._id)
        glut.glutSetWindowTitle(title.encode('ASCII'))

    def _vispy_set_size(self, w, h):
        # Set size of the widget or window
        glut.glutSetWindow(self._id)
        glut.glutReshapeWindow(w, h)

    def _vispy_set_position(self, x, y):
        # Set position of the widget or window. May have no effect for widgets
        glut.glutSetWindow(self._id)
        glut.glutPositionWindow(x, y)

    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        glut.glutSetWindow(self._id)
        if visible:
            glut.glutShowWindow()
        else:
            glut.glutHideWindow()

    def _vispy_update(self):
        # Invoke a redraw
        glut.glutSetWindow(self._id)
        glut.glutPostRedisplay()

    def _vispy_close(self):
        # Force the window or widget to shut down
        if self._closed:
            return
        self._vispy_canvas = None
        # sometimes the context is already destroyed
        try:
            # prevent segfaults during garbage col
            _set_close_fun(self._id, None)
        except Exception:
            pass
        self._closed = True
        self._vispy_set_visible(False)
        # Try destroying the widget. Not in close event, because it isnt called
        try:
            glut.glutDestroyWindow(self._id)
        except Exception:
            pass

    def _vispy_get_size(self):
        glut.glutSetWindow(self._id)
        w = glut.glutGet(glut.GLUT_WINDOW_WIDTH)
        h = glut.glutGet(glut.GLUT_WINDOW_HEIGHT)
        return w, h

    def _vispy_get_position(self):
        glut.glutSetWindow(self._id)
        x = glut.glutGet(glut.GLUT_WINDOW_X)
        y = glut.glutGet(glut.GLUT_WINDOW_Y)
        return x, y

    def _vispy_get_fullscreen(self):
        return self._fullscreen

    def _vispy_set_fullscreen(self, fullscreen):
        old_val = self._fullscreen
        self._fullscreen = bool(fullscreen)
        if old_val != self._fullscreen:
            if self._fullscreen:
                self._old_size = self._vispy_get_size()
                glut.glutFullScreen()
            else:
                self._vispy_set_size(*self._old_size)

    def on_resize(self, w, h):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.resize(size=(w, h))

    def on_close(self):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.close()

    def on_draw(self, dummy=None):
        if self._vispy_canvas is None:
            return
        #w = glut.glutGet(glut.GLUT_WINDOW_WIDTH)
        #h = glut.glutGet(glut.GLUT_WINDOW_HEIGHT)
        self._vispy_set_current()
        self._vispy_canvas.events.draw(region=None)  # (0, 0, w, h))

    def on_mouse_action(self, button, state, x, y):
        if self._vispy_canvas is None:
            return
        action = {glut.GLUT_UP: 'release', glut.GLUT_DOWN: 'press'}[state]
        mod = self._modifiers(False)

        if button < 3:
            # Mouse click event
            button = BUTTONMAP.get(button, 0)
            if action == 'press':
                self._vispy_mouse_press(pos=(x, y), button=button,
                                        modifiers=mod)
            else:
                self._vispy_mouse_release(pos=(x, y), button=button,
                                          modifiers=mod)

        elif button in (3, 4):
            # Wheel event
            deltay = 1.0 if button == 3 else -1.0
            self._vispy_canvas.events.mouse_wheel(pos=(x, y),
                                                  delta=(0.0, deltay),
                                                  modifiers=mod)

    def on_mouse_motion(self, x, y):
        if self._vispy_canvas is None:
            return
        self._vispy_mouse_move(
            pos=(x, y),
            modifiers=self._modifiers(False),
        )

    def on_key_press(self, key, x, y):
        key, text = self._process_key(key)
        self._vispy_canvas.events.key_press(key=key, text=text,
                                            modifiers=self._modifiers())

    def on_key_release(self, key, x, y):
        key, text = self._process_key(key)
        self._vispy_canvas.events.key_release(key=key, text=text,
                                              modifiers=self._modifiers())

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

    def _modifiers(self, query_now=True):
        if query_now:
            glutmod = glut.glutGetModifiers()
            mod = ()
            if glut.GLUT_ACTIVE_SHIFT & glutmod:
                mod += keys.SHIFT,
            if glut.GLUT_ACTIVE_CTRL & glutmod:
                mod += keys.CONTROL,
            if glut.GLUT_ACTIVE_ALT & glutmod:
                mod += keys.ALT,
            self._modifiers_cache = mod
        return self._modifiers_cache


# ------------------------------------------------------------------- timer ---

# Note: we could also build a timer using glutTimerFunc, but this causes
# trouble because timer callbacks appear to take precedence over all others.
# Thus, a fast timer can block new display events.
class TimerBackend(BaseTimerBackend):
    def __init__(self, vispy_timer):
        BaseTimerBackend.__init__(self, vispy_timer)
        self._schedule = list()
        glut.glutIdleFunc(self._idle_callback)
        # tell application instance about existence
        vispy_timer._app._backend._add_timer(self)

    def _idle_callback(self):
        now = ptime.time()
        new_schedule = []

        # see whether there are any timers ready
        while len(self._schedule) > 0 and self._schedule[0][0] <= now:
            timer = self._schedule.pop(0)[1]
            timer._vispy_timer._timeout()
            if timer._vispy_timer.running:
                new_schedule.append((now + timer._vispy_timer.interval, timer))

        # schedule next round of timeouts
        if len(new_schedule) > 0:
            self._schedule.extend(new_schedule)
            self._schedule.sort()

    def _vispy_start(self, interval):
        now = ptime.time()
        self._schedule.append((now + interval, self))

    def _vispy_stop(self):
        pass

    def _vispy_get_native_timer(self):
        return True  # glut has no native timer objects.
