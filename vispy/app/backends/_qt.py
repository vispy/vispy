# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
vispy backend for Qt (PySide and PyQt4).
"""

from __future__ import division

from ... import config
from ..base import BaseApplicationBackend, BaseCanvasBackend, BaseTimerBackend
from ...util import keys
from . import ATTEMPTED_BACKENDS
from ...util.six import text_type

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

BUTTONMAP = {0: 0, 1: 1, 2: 2, 4: 3, 8: 4, 16: 5}


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
        # Store so it won't be deleted, but not on a visvis object,
        # or an application may produce error when closed
        QtGui._qApp = app
        # Return
        return app


class CanvasBackend(QtOpenGL.QGLWidget, BaseCanvasBackend):

    """Qt backend for Canvas abstract class."""

    def __init__(self, *args, **kwargs):
        BaseCanvasBackend.__init__(self)
        QtOpenGL.QGLWidget.__init__(self, *args, **kwargs)
        self.setAutoBufferSwap(False)  # to make consistent with other backends
        self.setMouseTracking(True)

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
            self.show()
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


# class QtMouseEvent(MouseEvent):
# special subclass of MouseEvent for propagating acceptance info back to Qt.
#     @MouseEvent.handled.setter
#     def handled(self, val):
#         self._handled = val
#         if val:
#             self.qt_event.accept()
#         else:
#             self.qt_event.ignore()
class TimerBackend(BaseTimerBackend, QtCore.QTimer):

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
