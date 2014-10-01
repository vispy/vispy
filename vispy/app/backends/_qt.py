# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Base code for the Qt backends. Note that this is *not* (anymore) a
backend by itself! One has to explicitly use either PySide, PyQt4 or
PyQt5. Note that the automatic backend selection prefers a GUI toolkit
that is already imported.

The _pyside, _pyqt4 and _pyqt5 modules will import * from this module,
and also keep a ref to the module object. Note that if two of the
backends are used, this module is actually reloaded. This is a sorts
of poor mans "subclassing" to get a working version for both backends
using the same code.

Note that it is strongly discouraged to use the PySide/PyQt4/PyQt5
backends simultaneously. It is known to cause unpredictable behavior
and segfaults.
"""

from __future__ import division

from time import sleep, time
import sys

from ...util import logger
from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend)
from ...util import keys
from ...ext.six import text_type
from . import qt_lib


# -------------------------------------------------------------------- init ---

def _check_imports(lib):
    # Make sure no conflicting libraries have been imported.
    libs = ['PyQt4', 'PyQt5', 'PySide']
    libs.remove(lib)
    for lib2 in libs:
        lib2 += '.QtCore'
        if lib2 in sys.modules:
            raise RuntimeError("Refusing to import %s because %s is already "
                               "imported." % (lib, lib2))

# Get what qt lib to try. This tells us wheter this module is imported
# via _pyside or _pyqt4 or _pyqt5
if qt_lib == 'pyqt4':
    _check_imports('PyQt4')
    from PyQt4 import QtOpenGL
    from PyQt4 import QtGui, QtCore
elif qt_lib == 'pyqt5':
    _check_imports('PyQt5')
    from PyQt5 import QtOpenGL
    from PyQt5 import QtGui, QtCore, QtWidgets
elif qt_lib == 'pyside':
    _check_imports('PySide')
    from PySide import QtOpenGL
    from PySide import QtGui, QtCore
elif qt_lib:
    raise RuntimeError("Invalid value for qt_lib %r." % qt_lib)
else:
    raise RuntimeError("Module backends._qt should not be imported directly.")

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
BUTTONMAP = {0: 0, 1: 1, 2: 2, 4: 3, 8: 4, 16: 5}


# Properly log Qt messages
# Also, ignore spam about tablet input
def message_handler(msg_type, msg):
    if msg == ("QCocoaView handleTabletEvent: This tablet device is "
               "unknown (received no proximity event for it). Discarding "
               "event."):
        return
    else:
        logger.warning(msg)

try:
    QtCore.qInstallMsgHandler(message_handler)
except AttributeError:
    QtCore.qInstallMessageHandler(message_handler)  # PyQt5


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


# ------------------------------------------------------------- application ---

class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)

    def _vispy_get_backend_name(self):
        name = QtCore.__name__.split('.')[0]
        return name + ' (qt)'
    
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
        if hasattr(QtGui, 'QApplication'):
            app = QtGui.QApplication.instance()
            if app is None:
                app = QtGui.QApplication([''])
        else:
            # PyQt5
            app = QtWidgets.QApplication.instance()
            if app is None:
                app = QtWidgets.QApplication([''])
        # Store so it won't be deleted, but not on a vispy object,
        # or an application may produce error when closed.
        QtGui._qApp = app
        # Return
        return app


# ------------------------------------------------------------------ canvas ---

class CanvasBackend(BaseCanvasBackend, QtOpenGL.QGLWidget):

    """Qt backend for Canvas abstract class."""

    # args are for BaseCanvasBackend, kwargs are for us.
    def __init__(self, *args, **kwargs):
        BaseCanvasBackend.__init__(self, *args)
        # Maybe to ensure that exactly all arguments are passed?
        title, size, position, show, vsync, resize, dec, fs, parent, context, \
            = self._process_backend_kwargs(kwargs)
        self._initialized = False
        
        # Deal with context
        if not context.istaken:
            widget = kwargs.pop('shareWidget', None) or self
            context.take('qt', widget)
            glformat = _set_config(context.config)
            glformat.setSwapInterval(1 if vsync else 0)
            if widget is self:
                widget = None  # QGLWidget does not accept self ;)
        elif context.istaken == 'qt':
            widget = context.backend_canvas
            glformat = QtOpenGL.QGLFormat.defaultFormat()
            if 'shareWidget' in kwargs:
                raise RuntimeError('Cannot use vispy to share context and '
                                   'use built-in shareWidget.')
        else:
            raise RuntimeError('Different backends cannot share a context.')
        
        f = QtCore.Qt.Widget if dec else QtCore.Qt.FramelessWindowHint

        # first arg can be glformat, or a gl context
        QtOpenGL.QGLWidget.__init__(self, glformat, parent, widget, f)
        self._initialized = True
        if not self.isValid():
            raise RuntimeError('context could not be created')
        self.setAutoBufferSwap(False)  # to make consistent with other backends
        self.setMouseTracking(True)
        self._vispy_set_title(title)
        self._vispy_set_size(*size)
        if fs is not False:
            if fs is not True:
                logger.warning('Cannot specify monitor number for Qt '
                               'fullscreen, using default')
            self._fullscreen = True
        else:
            self._fullscreen = False
        if not resize:
            self.setFixedSize(self.size())
        if position is not None:
            self._vispy_set_position(*position)
        if show:
            self._vispy_set_visible(True)
    
    def _vispy_set_current(self):
        if self._vispy_canvas is None:
            return  # todo: can we get rid of this now?
        if self.isValid():
            self._vispy_context.set_current(False)  # Mark as current
            self.makeCurrent()
    
    def _vispy_warmup(self):
        etime = time() + 0.25
        while time() < etime:
            sleep(0.01)
            self._vispy_set_current()
            self._vispy_canvas.app.process_events()
    
    def _vispy_swap_buffers(self):
        # Swap front and back buffer
        if self._vispy_canvas is None:
            return
        self.swapBuffers()

    def _vispy_set_title(self, title):
        # Set the window title. Has no effect for widgets
        if self._vispy_canvas is None:
            return
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
            if self._fullscreen:
                self.showFullScreen()
            else:
                self.showNormal()
        else:
            self.hide()

    def _vispy_set_fullscreen(self, fullscreen):
        self._fullscreen = bool(fullscreen)
        self._vispy_set_visible(True)

    def _vispy_get_fullscreen(self):
        return self._fullscreen

    def _vispy_update(self):
        if self._vispy_canvas is None:
            return
        # Invoke a redraw
        self.update()

    def _vispy_close(self):
        # Force the window or widget to shut down
        self.close()
        self.doneCurrent()
        self.context().reset()

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
        self._vispy_canvas.events.draw(region=None)

    def closeEvent(self, ev):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.close()

    def sizeHint(self):
        return self.size()

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
        self._keyEvent(self._vispy_canvas.events.key_press, ev)

    def keyReleaseEvent(self, ev):
        self._keyEvent(self._vispy_canvas.events.key_release, ev)

    def _keyEvent(self, func, ev):
        # evaluates the keycode of qt, and transform to vispy key.
        key = int(ev.key())
        if key in KEYMAP:
            key = KEYMAP[key]
        elif key >= 32 and key <= 127:
            key = keys.Key(chr(key))
        else:
            key = None
        mod = self._modifiers(ev)
        func(native=ev, key=key, text=text_type(ev.text()), modifiers=mod)

    def _modifiers(self, event):
        # Convert the QT modifier state into a tuple of active modifier keys.
        mod = ()
        qtmod = event.modifiers()
        for q, v in ([QtCore.Qt.ShiftModifier, keys.SHIFT],
                     [QtCore.Qt.ControlModifier, keys.CONTROL],
                     [QtCore.Qt.AltModifier, keys.ALT],
                     [QtCore.Qt.MetaModifier, keys.META]):
            if q & qtmod:
                mod += (v,)
        return mod


# ------------------------------------------------------------------- timer ---

class TimerBackend(BaseTimerBackend, QtCore.QTimer):

    def __init__(self, vispy_timer):
        # Make sure there is an app
        app = ApplicationBackend()
        app._vispy_get_native_app()
        # Init
        BaseTimerBackend.__init__(self, vispy_timer)
        QtCore.QTimer.__init__(self)
        self.timeout.connect(self._vispy_timeout)

    def _vispy_start(self, interval):
        self.start(interval * 1000.)

    def _vispy_stop(self):
        self.stop()

    def _vispy_timeout(self):
        self._vispy_timer._timeout()
