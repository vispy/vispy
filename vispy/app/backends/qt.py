from vispy.event import MouseEvent
from vispy import app
from vispy import keys

import vispy
qt_lib = vispy.config['qt_lib']
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
    raise Exception("Do not recognize Qt library '%s'. Options are 'pyqt', 'pyside', or 'any' (see vispy.config['qt_lib'])." % str(qt_lib))


#KEYMAP = {
    #QtCore.Qt.Key_Shift: keys.SHIFT,
    #QtCore.Qt.Key_Control: keys.CONTROL,
    #QtCore.Qt.Key_Alt: keys.ALT,
    #QtCore.Qt.ShiftModifier: keys.SHIFT,
    #QtCore.Qt.ControlModifier: keys.CONTROL,
    #QtCore.Qt.AltModifier: keys.ALT,
    
    #QtCore.Qt.Key_Left: keys.LEFT,
    #QtCore.Qt.Key_Up: keys.UP,
    #QtCore.Qt.Key_Right: keys.RIGHT,
    #QtCore.Qt.Key_Down: keys.DOWN,
    #QtCore.Qt.Key_PageUp: keys.PAGEUP,
    #QtCore.Qt.Key_PageDown: keys.PAGEDOWN,
    #QtCore.Qt.Key_Escape: keys.ESCAPE,
    #QtCore.Qt.Key_Delete: keys.DELETE,
    #QtCore.Qt.Key_Backspace: keys.BACKSPACE,
    
    #QtCore.Qt.Key_Space: keys.SPACE,
    #QtCore.Qt.Key_Enter: keys.ENTER,
    #QtCore.Qt.Key_Return: keys.ENTER,
#}


class ApplicationBackend(app.ApplicationBackend):
    
    def __init__(self):
        app.ApplicationBackend.__init__(self)
    
    def _vispy_get_backend_name(self):
        return 'qt' #todo: pyside or PyQt? (must support both; see vispy.config['qt_lib'])
    
    def _vispy_process_events(self):
        app = self._vispy_get_native_app()
        app.flush()
        app.processEvents()
    
    def _vispy_run(self):
        app = self._vispy_get_native_app()
        if hasattr(app, '_in_event_loop') and app._in_event_loop:
            pass # Already in event loop
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



class CanvasBackend(QtOpenGL.QGLWidget, app.CanvasBackend):
    """Qt backend for Canvas abstract class."""
    
    def __init__(self, vispy_canvas, *args, **kwargs):
        QtOpenGL.QGLWidget.__init__(self, *args, **kwargs)
        app.CanvasBackend.__init__(self, vispy_canvas)
    
    
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
    
    def _vispy_set_location(self, x, y):
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
    
    def _vispy_get_geometry(self):
        # Should return widget (x, y, w, h)
        g = self.geometry()
        return (g.x(), g.y(), g.width(), g.height())
    
    
    
    def initializeGL(self):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.initialize()
        
    def resizeGL(self, w, h):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.resize(size=(w,h)) # todo: new event?

    def paintGL(self):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.paint()
            #region=(0, 0, self.width(), self.height()))
        
    def mousePressEvent(self, ev):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.mouse_press(
            native=ev,
            pos=(ev.pos().x(), ev.pos().y()),
            button=int(ev.button()),
            modifiers = self._modifiers(ev),
            )
            
    def mouseReleaseEvent(self, ev):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.mouse_release(
            native=ev,
            pos=(ev.pos().x(), ev.pos().y()),
            button=int(ev.button()),
            modifiers = self._modifiers(ev),
            )

    def mouseMoveEvent(self, ev):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.mouse_move(
            native=ev,
            pos=(ev.pos().x(), ev.pos().y()),
            modifiers = self._modifiers(ev),
            )
        
    def wheelEvent(self, ev):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.mouse_wheel(
            native=ev,
            delta=ev.delta(),
            pos=(ev.pos().x(), ev.pos().y()),
            modifiers = self._modifiers(ev),
            )
    
    
    def keyPressEvent(self, ev):
        self._vispy_canvas.events.key_press(
            key_id = ev.key(), #self._processKey(ev), 
            text = str(ev.text()),
            modifiers = self._modifiers(ev),
            auto_repeat=ev.isAutoRepeat(),
            )
    
    def keyReleaseEvent(self, ev):
        #if ev.isAutoRepeat():
            #return # Skip release auto repeat events
        self._vispy_canvas.events.key_release(
            key_id = ev.key(), #self._processKey(ev), 
            text = str(ev.text()),
            modifiers = self._modifiers(ev),
            auto_repeat=ev.isAutoRepeat(),
            )
    
    #def _processKey(self, event):
        ## evaluates the keycode of qt, and transform to vispy key.
        #key = event.key()
        #return KEYMAP.get(key, key)
    
    def _modifiers(self, event):
        # Convert the QT modifier state into a tuple of active modifier keys.
        mod = ()
        qtmod = event.modifiers()
        if QtCore.Qt.ShiftModifier & qtmod:
            mod += keys['Shift'],
        if QtCore.Qt.ControlModifier & qtmod:
            mod += keys['Control'],
        if QtCore.Qt.AltModifier & qtmod:
            mod += keys['Alt'],
        return mod



class QtMouseEvent(MouseEvent):
    ## special subclass of MouseEvent for propagating acceptance info back to Qt.
    @MouseEvent.handled.setter
    def handled(self, val):
        self._handled = val
        if val:
            self.qt_event.accept()
        else:
            self.qt_event.ignore()


class TimerBackend(app.TimerBackend, QtCore.QTimer):
    def __init__(self, vispy_timer):
        if QtGui.QApplication.instance() is None:
            global QAPP
            QAPP = QtGui.QApplication([])
        app.TimerBackend.__init__(self, vispy_timer)
        QtCore.QTimer.__init__(self)
        self.timeout.connect(self._vispy_timeout)
        
    def _vispy_start(self, interval):
        self.start(interval*1000.)
        
    def _vispy_stop(self):
        self.stop()
        
    def _vispy_timeout(self):
        self._vispy_timer._timeout()
    


