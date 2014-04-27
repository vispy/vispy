# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
vispy backend for Qt (PySide and PyQt4).
"""

from __future__ import division
from time import sleep, time

from ... import config
from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend, BaseSharedContext)
from ...util import keys
from . import ATTEMPTED_BACKENDS
from ...util.six import text_type
from ...util import logger

# Get what qt lib to try
if len(ATTEMPTED_BACKENDS):
    qt_lib = ATTEMPTED_BACKENDS[-1].lower()
    if qt_lib.lower() == 'qt':
        qt_lib = config['qt_lib'].lower()
    # in case the last app we ran was something else (e.g., Pyglet)
    if qt_lib not in ['pyqt', 'pyqt4', 'pyside', 'qt']:
        qt_lib = 'any'
else:
    qt_lib = 'any'

# -------------------------------------------------------------------- init ---

try:
    # Import PySide or PyQt4
    if qt_lib in ('any', 'qt'):
        try:
            from PyQt4 import QtGui, QtCore, QtOpenGL
        except ImportError:
            from PySide import QtGui, QtCore, QtOpenGL
    elif qt_lib in ('pyqt', 'pyqt4'):
        from PyQt4 import QtGui, QtCore, QtOpenGL
    elif qt_lib == 'pyside':
        from PySide import QtGui, QtCore, QtOpenGL
    else:
        raise Exception("Do not recognize Qt library '%s'. Options are "
                        "'pyqt4', 'pyside', or 'qt'])." % str(qt_lib))

    # todo: add support for distinguishing left and right shift/ctrl/alt keys.
    # Linux scan codes:  (left, right)
    #   Shift  50, 62
    #   Ctrl   37, 105
    #   Alt    64, 108
    KEYMAP = {
        QtCore.Qt.Key_Shift: keys.SHIFT,
        QtCore.Qt.Key_Control: keys.CONTROL,
        QtCore.Qt.Key_Alt: keys.ALT,
        QtCore.Qt.Key_AltGr: keys.ALT,
        QtCore.Qt.Key_Meta: keys.META,

        QtCore.Qt.Key_Left: keys.LEFT,
        QtCore.Qt.Key_Up: keys.UP,
        QtCore.Qt.Key_Right: keys.RIGHT,
        QtCore.Qt.Key_Down: keys.DOWN,
        QtCore.Qt.Key_PageUp: keys.PAGEUP,
        QtCore.Qt.Key_PageDown: keys.PAGEDOWN,

        QtCore.Qt.Key_Insert: keys.INSERT,
        QtCore.Qt.Key_Delete: keys.DELETE,
        QtCore.Qt.Key_Home: keys.HOME,
        QtCore.Qt.Key_End: keys.END,

        QtCore.Qt.Key_Escape: keys.ESCAPE,
        QtCore.Qt.Key_Backspace: keys.BACKSPACE,

        QtCore.Qt.Key_F1: keys.F1,
        QtCore.Qt.Key_F2: keys.F2,
        QtCore.Qt.Key_F3: keys.F3,
        QtCore.Qt.Key_F4: keys.F4,
        QtCore.Qt.Key_F5: keys.F5,
        QtCore.Qt.Key_F6: keys.F6,
        QtCore.Qt.Key_F7: keys.F7,
        QtCore.Qt.Key_F8: keys.F8,
        QtCore.Qt.Key_F9: keys.F9,
        QtCore.Qt.Key_F10: keys.F10,
        QtCore.Qt.Key_F11: keys.F11,
        QtCore.Qt.Key_F12: keys.F12,

        QtCore.Qt.Key_Space: keys.SPACE,
        QtCore.Qt.Key_Enter: keys.ENTER,
        QtCore.Qt.Key_Return: keys.ENTER,
        QtCore.Qt.Key_Tab: keys.TAB,
    }
except Exception as exp:
    available = False
    why_not = str(exp)

    class _QGLWidget(object):
        pass

    class _QTimer(object):
        pass
else:
    available = True
    why_not = None
    _QGLWidget = QtOpenGL.QGLWidget
    _QTimer = QtCore.QTimer
    if hasattr(QtCore, 'PYQT_VERSION_STR'):
        has_uic = True
        which = ('PyQt4', QtCore.PYQT_VERSION_STR, QtCore.QT_VERSION_STR)
    else:
        has_uic = False
        import PySide
        which = ('PySide', PySide.__version__, QtCore.__version__)

BUTTONMAP = {0: 0, 1: 1, 2: 2, 4: 3, 8: 4, 16: 5}

# -------------------------------------------------------------- capability ---

capability = dict(  # things that can be set by the backend
    title=True,
    size=True,
    position=True,
    show=True,
    decorate=True,
    resizable=True,
    vsync=True,
    context=False,  # XXX causes segfaults currently :(
    multi_window=True,
    scroll=True,
)


# ------------------------------------------------------- set_configuration ---
def _set_config(c):
    """Set the OpenGL configuration"""
    glformat = QtOpenGL.QGLFormat()
    glformat.setRedBufferSize(c['red_size'])
    glformat.setGreenBufferSize(c['green_size'])
    glformat.setBlueBufferSize(c['blue_size'])
    glformat.setAlphaBufferSize(c['alpha_size'])
    glformat.setAccum(False)
    glformat.setRgba(True)
    glformat.setDoubleBuffer(True if c['double_buffer'] else False)
    glformat.setDepth(True if c['depth_size'] else False)
    glformat.setDepthBufferSize(c['depth_size'] if c['depth_size'] else 0)
    glformat.setStencil(True if c['stencil_size'] else False)
    glformat.setStencilBufferSize(c['stencil_size'] if c['stencil_size']
                                  else 0)
    glformat.setSampleBuffers(True if c['samples'] else False)
    glformat.setSamples(c['samples'] if c['samples'] else 0)
    glformat.setStereo(c['stereo'])
    return glformat


class SharedContext(BaseSharedContext):
    _backend = 'qt'


# ------------------------------------------------------------- application ---

class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)

    def _vispy_get_backend_name(self):
        if 'pyside' in QtCore.__name__.lower():
            return 'PySide (qt)'
        else:
            return 'PyQt4 (qt)'

    def _vispy_process_events(self):
        app = self._vispy_get_native_app()
        app.flush()
        app.processEvents()

    def _vispy_run(self):
        app = self._vispy_get_native_app()
        if hasattr(app, '_in_event_loop') and app._in_event_loop:
            pass  # Already in event loop
        else:
            return app.exec_()

    def _vispy_quit(self):
        return self._vispy_get_native_app().quit()

    def _vispy_get_native_app(self):
        # Get native app in save way. Taken from guisupport.py
        app = QtGui.QApplication.instance()
        if app is None:
            app = QtGui.QApplication([''])
        # Store so it won't be deleted, but not on a vispy object,
        # or an application may produce error when closed
        QtGui._qApp = app
        # Return
        return app


# ------------------------------------------------------------------ canvas ---

class CanvasBackend(_QGLWidget, BaseCanvasBackend):

    """Qt backend for Canvas abstract class."""

    def __init__(self, *args, **kwargs):
        BaseCanvasBackend.__init__(self, capability, SharedContext)
        title, size, position, show, vsync, resize, dec, fs, context = \
            self._process_backend_kwargs(kwargs)
        if isinstance(context, dict):
            glformat = _set_config(context)
            glformat.setSwapInterval(1 if vsync else 0)
        else:
            glformat = context.value
        f = QtCore.Qt.Widget if dec else QtCore.Qt.FramelessWindowHint
        parent = kwargs.pop('parent', None)
        widget = kwargs.pop('shareWidget', None)
        # first arg can be glformat, or a shared context
        QtOpenGL.QGLWidget.__init__(self, glformat, parent, widget, f)
        self.__del__ = self._check_destroy  # only set __del__ once init'ed
        if not self.isValid():
            raise RuntimeError('context could not be created')
        self.setAutoBufferSwap(False)  # to make consistent with other backends
        self.setMouseTracking(True)
        self._vispy_set_title(title)
        self._vispy_set_size(*size)
        if fs:
            if not isinstance(fs, bool):
                logger.warn('Cannot specify monitor for Qt fullscreen, '
                            'using default')
            self._fs = True
        else:
            self._fs = False
        if not resize:
            self.setFixedSize(self.size())
        if position is not None:
            self._vispy_set_position(*position)
        if show:
            self._vispy_set_visible(True)

    @property
    def _vispy_context(self):
        """Context to return for sharing"""
        return SharedContext(self.context())

    def _vispy_warmup(self):
        etime = time() + 0.25
        while time() < etime:
            sleep(0.01)
            self._vispy_set_current()
            self._vispy_canvas.app.process_events()

    def _vispy_set_current(self):
        # Make this the current context
        self.makeCurrent()

    def _vispy_swap_buffers(self):
        # Swap front and back buffer
        self.swapBuffers()

    def _vispy_set_title(self, title):
        # Set the window title. Has no effect for widgets
        self.setWindowTitle(title)

    def _vispy_set_size(self, w, h):
        # Set size of the widget or window
        self.resize(w, h)

    def _vispy_set_position(self, x, y):
        # Set location of the widget or window. May have no effect for widgets
        self.move(x, y)

    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        if visible:
            self.showFullScreen() if self._fs else self.show()
        else:
            self.hide()

    def _vispy_update(self):
        # Invoke a redraw
        self.update()

    def _vispy_close(self):
        # Force the window or widget to shut down
        self.close()

    def _vispy_get_position(self):
        g = self.geometry()
        return g.x(), g.y()

    def _vispy_get_size(self):
        g = self.geometry()
        return g.width(), g.height()

    def initializeGL(self):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.initialize()

    def resizeGL(self, w, h):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.resize(size=(w, h))

    def paintGL(self):
        if self._vispy_canvas is None:
            return
        # (0, 0, self.width(), self.height()))
        self._vispy_set_current()
        self._vispy_canvas.events.paint(region=None)

    def closeEvent(self, ev):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.close()

    def mousePressEvent(self, ev):
        if self._vispy_canvas is None:
            return
        self._vispy_mouse_press(
            native=ev,
            pos=(ev.pos().x(), ev.pos().y()),
            button=BUTTONMAP.get(ev.button(), 0),
            modifiers = self._modifiers(ev),
        )

    def mouseReleaseEvent(self, ev):
        if self._vispy_canvas is None:
            return
        self._vispy_mouse_release(
            native=ev,
            pos=(ev.pos().x(), ev.pos().y()),
            button=BUTTONMAP[ev.button()],
            modifiers = self._modifiers(ev),
        )

    def mouseMoveEvent(self, ev):
        if self._vispy_canvas is None:
            return
        self._vispy_mouse_move(
            native=ev,
            pos=(ev.pos().x(), ev.pos().y()),
            modifiers=self._modifiers(ev),
        )

    def wheelEvent(self, ev):
        if self._vispy_canvas is None:
            return
        # Get scrolling
        deltax, deltay = 0.0, 0.0
        if ev.orientation == QtCore.Qt.Horizontal:
            deltax = ev.delta() / 120.0
        else:
            deltay = ev.delta() / 120.0
        # Emit event
        self._vispy_canvas.events.mouse_wheel(
            native=ev,
            delta=(deltax, deltay),
            pos=(ev.pos().x(), ev.pos().y()),
            modifiers=self._modifiers(ev),
        )

    def keyPressEvent(self, ev):
        self._vispy_canvas.events.key_press(
            native=ev,
            key=self._processKey(ev),
            text=text_type(ev.text()),
            modifiers=self._modifiers(ev),
        )

    def keyReleaseEvent(self, ev):
        # if ev.isAutoRepeat():
            # return # Skip release auto repeat events
        self._vispy_canvas.events.key_release(
            native=ev,
            key=self._processKey(ev),
            text=text_type(ev.text()),
            modifiers=self._modifiers(ev),
        )

    def _processKey(self, event):
        # evaluates the keycode of qt, and transform to vispy key.
        key = int(event.key())
        if key in KEYMAP:
            return KEYMAP[key]
        elif key >= 32 and key <= 127:
            return keys.Key(chr(key))
        else:
            return None

    def _modifiers(self, event):
        # Convert the QT modifier state into a tuple of active modifier keys.
        mod = ()
        qtmod = event.modifiers()
        if QtCore.Qt.ShiftModifier & qtmod:
            mod += keys.SHIFT,
        if QtCore.Qt.ControlModifier & qtmod:
            mod += keys.CONTROL,
        if QtCore.Qt.AltModifier & qtmod:
            mod += keys.ALT,
        if QtCore.Qt.MetaModifier & qtmod:
            mod += keys.META,
        return mod

    def _check_destroy(self):
        # Destroy if this is a toplevel widget
        if self.parent() is None:
            self.destroy()
        if hasattr(QtOpenGL.QGLWidget, '__del__'):
            QtOpenGL.QGLWidget.__del__(self)


# ------------------------------------------------------------------- timer ---

class TimerBackend(BaseTimerBackend, _QTimer):

    def __init__(self, vispy_timer):
        if QtGui.QApplication.instance() is None:
            global QAPP
            QAPP = QtGui.QApplication([])
        BaseTimerBackend.__init__(self, vispy_timer)
        QtCore.QTimer.__init__(self)
        self.timeout.connect(self._vispy_timeout)

    def _vispy_start(self, interval):
        self.start(interval * 1000.)

    def _vispy_stop(self):
        self.stop()

    def _vispy_timeout(self):
        self._vispy_timer._timeout()
