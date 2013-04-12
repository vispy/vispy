from pyvis.event import Event
from pyvis import app


import pyvis
qt_lib = pyvis.config['qt_lib']
if qt_lib == 'any':
    try: 
        from PyQt4 import QtGui, QtCore, QtOpenGL
    except ImportError:
        from PySide import QtGui, QtCore, QtOpenGL
elif qt_lib == 'pyqt':
    from PyQt4 import QtGui, QtCore
elif qt_lib == 'pyside':
    from PySide import QtGui, QtCore
else:
    raise Exception("Do not recognize Qt library '%s'. Options are 'pyqt', 'pyside', or 'any' (see pyvis.config['qt_lib'])." % str(qt_lib))




class ApplicationBackend(app.ApplicationBackend):
    
    def __init__(self):
        app.ApplicationBackend.__init__(self)
    
    def _pyvis_get_backend_name(self):
        return 'Qt' #todo: pyside or PyQt?
    
    def _pyvis_process_events(self):
        app = self._pyvis_get_native_app()
        app.flush()
        app.processEvents()
    
    def _pyvis_run(self):
        app = self._pyvis_get_native_app()
        if hasattr(app, '_in_event_loop') and app._in_event_loop:
            pass # Already in event loop
        else:
            return app.exec_()
    
    def _pyvis_quit(self):
        return self._pyvis_get_native_app().quit()
    
    def _pyvis_get_native_app(self):
        # Get native app in save way. Taken from guisupport.py
        app = QtGui.QApplication.instance()
        if app is None:
            app = QtGui.QApplication([''])
        # Store so it won't be deleted, but not on a visvis object,
        # or an application may produce error when closed
        QtGui._qApp = app
        # Return
        return app




class CanvasBackend(QtOpenGL.QGLWidget, app.CanvasBackend):
    """Qt backend for Canvas abstract class."""
    
    def __init__(self, parent=None):
        # before creating widget, make sure we have a QApplication
        pyvis.app.default_app.native
        
        app.CanvasBackend.__init__(self)
        QtOpenGL.QGLWidget.__init__(self, parent)

        
    @property
    def _pyvis_geometry(self):
        g = self.geometry()
        return (g.x(), g.y(), g.width(), g.height())
    
    def _pyvis_resize(self, w, h):
        self.resize(w, h)
        
    def _pyvis_show(self):
        self.show()
        
    def _pyvis_update(self):
        self.update()
    
    def initializeGL(self):
        if self._pyvis_canvas is None:
            return
        self._pyvis_canvas.events.initialize()
        
    def resizeGL(self, w, h):
        if self._pyvis_canvas is None:
            return
        ev = Event(size=(w,h))
        self._pyvis_canvas.events.resize(ev)

    def paintGL(self):
        if self._pyvis_canvas is None:
            return
        ev = Event(region=(0, 0, self.width(), self.height()))
        self._pyvis_canvas.events.paint(ev)
        
    def mousePressEvent(self, ev):
        if self._pyvis_canvas is None:
            return
        ev2 = QtMouseEvent(
            action='press', 
            qt_event=ev,
            pos=(ev.pos().x(), ev.pos().y()),
            button=int(ev.button()),
            )
        self._pyvis_canvas.events.mouse_press(ev2)
            
    def mouseReleaseEvent(self, ev):
        if self._pyvis_canvas is None:
            return
        ev2 = QtMouseEvent(
            action='release', 
            qt_event=ev,
            pos=(ev.pos().x(), ev.pos().y()),
            button=int(ev.button()),
            )
        self._pyvis_canvas.events.mouse_release(ev2)

    def mouseMoveEvent(self, ev):
        if self._pyvis_canvas is None:
            return
        ev2 = QtMouseEvent(
            action='move', 
            qt_event=ev,
            pos=(ev.pos().x(), ev.pos().y()),
            )
        self._pyvis_canvas.events.mouse_move(ev2)
        
    def wheelEvent(self, ev):
        if self._pyvis_canvas is None:
            return
        ev2 = Event( 
            action='wheel', 
            qt_event=ev,
            delta=ev.delta(),
            pos=(ev.pos().x(), ev.pos().y()),
            )
        self._pyvis_canvas.events.mouse_wheel(ev2)
    
    
    def keyPressEvent(self, event):      
        key = self._processKey(event)
        text = str(event.text())
        #self.figure._GenerateKeyEvent('keydown', key, text, modifiers(event))
        # todo: modifiers
        self._pyvis_canvas.events.key_press(action='press', key=key, text=text)
    
    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return # Skip release auto repeat events
        key = self._processKey(event)
        text = str(event.text())
        self._pyvis_canvas.events.key_release(action='release', key=key, text=text)
    
    def _processKey(self,event):
        """ evaluates the keycode of qt, and transform to visvis key.
        """
        key = event.key()
        # special cases for shift control and alt -> map to 17 18 19
        if key in KEYMAP:
            return KEYMAP[key]
        else:
            return key 


class QtMouseEvent(Event):
    ## special subclass of Event for propagating acceptance info back to Qt.
    def accept(self):
        Event.accept(self)
        self.qt_event.accept()


# todo: define constants for pyvis
KEYMAP = {}
#             {  QtCore.Qt.Key_Shift: constants.KEY_SHIFT, 
#             QtCore.Qt.Key_Alt: constants.KEY_ALT,
#             QtCore.Qt.Key_Control: constants.KEY_CONTROL,
#             QtCore.Qt.Key_Left: constants.KEY_LEFT,
#             QtCore.Qt.Key_Up: constants.KEY_UP,
#             QtCore.Qt.Key_Right: constants.KEY_RIGHT,
#             QtCore.Qt.Key_Down: constants.KEY_DOWN,
#             QtCore.Qt.Key_PageUp: constants.KEY_PAGEUP,
#             QtCore.Qt.Key_PageDown: constants.KEY_PAGEDOWN,
#             QtCore.Qt.Key_Enter: constants.KEY_ENTER,
#             QtCore.Qt.Key_Return: constants.KEY_ENTER,
#             QtCore.Qt.Key_Escape: constants.KEY_ESCAPE,
#             QtCore.Qt.Key_Delete: constants.KEY_DELETE
#             }


class TimerBackend(app.TimerBackend, QtCore.QTimer):
    def __init__(self, timer):
        if QtGui.QApplication.instance() is None:
            global QAPP
            QAPP = QtGui.QApplication([])
        app.TimerBackend.__init__(self, timer)
        QtCore.QTimer.__init__(self)
        self.timeout.connect(self._pyvis_timeout)
        
    def _pyvis_start(self, interval):
        self.start(interval*1000.)
        
    def _pyvis_stop(self):
        self.stop()
        
    def _pyvis_timeout(self):
        self._pyvis_timer._timeout()
    
    def _pyvis_run(self):
        return QtGui.QApplication.exec_()

    def _pyvis_quit(self):
        return QtGui.QApplication.quit()


