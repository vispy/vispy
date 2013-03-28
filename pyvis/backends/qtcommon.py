# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" The QT4 backend.


"""
import os

import visvis
from visvis import BaseFigure, events, constants
from visvis.core.misc import getResourceDir

# Load Qt libs
qtlib = visvis.backends.qtlib
if qtlib == 'pyside':
    from PySide import QtCore, QtGui, QtOpenGL
elif qtlib == 'pyqt4':
    from PyQt4 import QtCore, QtGui, QtOpenGL
else:
    raise ImportError('Cannot import Qt: invalid qtlib specified "%s".' %qtlib)



# NOTICE: OpenGl some problems on Ubuntu (probably due gnome).
# The drawing of the frame and background seems sometimes be done
# seperate from the opengl drawings. This means that sometimes the
# OpenGl stuff is drawn while the frame is not, which results in stuff
# hangin in "mid-air". Or while dragging the whole window, the frame
# is drawn, but in it is either rubish (qt) or gray bg (wx). When the
# frame is not visible, it is still there (you can still resize etc.)
# This is a known bug of the X Server: 
# https://wiki.ubuntu.com/RedirectedDirectRendering
# A solution while the bug is not fixed is to set the visual effects off 
# in System > Preferences > Appearance.
# Also note tha wx seems the less affected backend (there is a small fix
# by redrawing on a Activate event which helps a lot)



KEYMAP = {  QtCore.Qt.Key_Shift: constants.KEY_SHIFT, 
            QtCore.Qt.Key_Alt: constants.KEY_ALT,
            QtCore.Qt.Key_Control: constants.KEY_CONTROL,
            QtCore.Qt.Key_Left: constants.KEY_LEFT,
            QtCore.Qt.Key_Up: constants.KEY_UP,
            QtCore.Qt.Key_Right: constants.KEY_RIGHT,
            QtCore.Qt.Key_Down: constants.KEY_DOWN,
            QtCore.Qt.Key_PageUp: constants.KEY_PAGEUP,
            QtCore.Qt.Key_PageDown: constants.KEY_PAGEDOWN,
            QtCore.Qt.Key_Enter: constants.KEY_ENTER,
            QtCore.Qt.Key_Return: constants.KEY_ENTER,
            QtCore.Qt.Key_Escape: constants.KEY_ESCAPE,
            QtCore.Qt.Key_Delete: constants.KEY_DELETE
            }

# Make uppercase letters be lowercase
for i in range(ord('A'), ord('Z')):
    KEYMAP[i] = i+32


def modifiers(event):
    """Convert the QT modifier state into a tuple of active modifier keys."""
    mod = ()
    qtmod = event.modifiers()
    if QtCore.Qt.ShiftModifier & qtmod:
        mod += constants.KEY_SHIFT,
    if QtCore.Qt.ControlModifier & qtmod:
        mod += constants.KEY_CONTROL,
    if QtCore.Qt.AltModifier & qtmod:
        mod += constants.KEY_ALT,
    return mod


class GLWidget(QtOpenGL.QGLWidget):
    """ An OpenGL widget inheriting from QtOpenGL.QGLWidget
    to pass events in the right way to the wrapping Figure class.
    """
    
    def __init__(self, figure, parent, *args):
        QtOpenGL.QGLWidget.__init__(self, parent, *args)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose) # keep cleaned up
        self.figure = figure
        # Note that the default QGLFormat has double buffering enabled.
        
        # Set icon
        try:
            iconFile = os.path.join(getResourceDir(), 'visvis_icon_%s.png' % qtlib)
            icon = QtGui.QIcon()
            icon.addFile(iconFile, QtCore.QSize(16,16))
            self.setWindowIcon(icon)
        except Exception:
            pass
        
        # enable mouse tracking so mousemove events are always fired.        
        self.setMouseTracking(True)
        
        # enable getting keyboard focus
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFocus() # make the widget have focus...
    
    
    def mousePressEvent(self, event):
        but = 0
        if event.button() == QtCore.Qt.LeftButton:
            but = 1
        elif event.button() == QtCore.Qt.RightButton:
            but = 2
        x, y = event.x(), event.y()
        self.figure._GenerateMouseEvent('down', x, y, but, modifiers(event))
    
    def mouseReleaseEvent(self, event):
        but = 0
        if event.button() == QtCore.Qt.LeftButton:
            but = 1
        elif event.button() == QtCore.Qt.RightButton:
            but = 2
        x, y = event.x(), event.y()
        self.figure._GenerateMouseEvent('up', x, y, but, modifiers(event))
    
    def mouseDoubleClickEvent(self, event):
        but = 0
        if event.button() == QtCore.Qt.LeftButton:
            but = 1
        elif event.button() == QtCore.Qt.RightButton:
            but = 2
        x, y = event.x(), event.y()
        self.figure._GenerateMouseEvent('double', x, y, but, modifiers(event))
    
    def mouseMoveEvent(self, event):
        if self.figure:
            # fire event   
            x, y = event.x(), event.y()
            self.figure._GenerateMouseEvent('motion', x, y, 0, modifiers(event))
    
    def wheelEvent(self, event):
        # Get number of steps
        numDegrees = event.delta() / 8.0
        numSteps = numDegrees / 15.0
        if event.orientation() == QtCore.Qt.Vertical:
            horizontal, vertical = 0, numSteps
        else:
            horizontal, vertical = numSteps, 0
        # fire event   
        x, y = event.x(), event.y()
        self.figure._GenerateMouseEvent('scroll', x, y, horizontal, vertical, modifiers(event))
    
    def keyPressEvent(self, event):      
        key = self._ProcessKey(event)
        text = str(event.text())
        self.figure._GenerateKeyEvent('keydown', key, text, modifiers(event))
    
    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return # Skip release auto repeat events
        key = self._ProcessKey(event)
        text = str(event.text())
        self.figure._GenerateKeyEvent('keyup', key, text, modifiers(event))
    
    def _ProcessKey(self,event):
        """ evaluates the keycode of qt, and transform to visvis key.
        """
        key = event.key()
        
        # special cases for shift control and alt -> map to 17 18 19
        if key in KEYMAP:
            return KEYMAP[key]
        else:
            return key
    
    def enterEvent(self, event):
        if self.figure:            
            ev = self.figure.eventEnter
            ev.Set(0,0,0)
            ev.Fire()
    
    def leaveEvent(self, event):
        if self.figure:
            ev = self.figure.eventLeave
            ev.Set(0,0,0)
            ev.Fire()
    
#     def resizeEvent(self, event):
#         """ QT event when the widget is resized.
#         """        
#         self.figure._OnResize()
    
    def closeEvent(self, event):
        if self.figure:
            self.figure.Destroy()
        event.accept()

    def focusInEvent (self, event):
        if self.figure:
            BaseFigure._currentNr = self.figure.nr
    
    
    def initializeGL(self):
        pass # no need
    
    def resizeGL(self, w, h):
        # This does not work if we implement resizeEvent
        self.figure._OnResize()
    
    def paintEvent(self,event):
        # Use this rather than paintGL, because the latter also swaps buffers,
        # while visvis already does that.
        # We could use self.setAutoBufferSwap(False), but it seems not to help.
        self.figure.OnDraw()
    
# This is to help draw the frame (see bug above), but I guess one should
# simply disable it's visual effects
#     def moveEvent(self, event):
#         self.update()
        
    def showEvent(self, event):
        # Force a redraw. In some applications that have stuff that takes
        # a while to draw, the content of the OpenGL widget is simply
        # fully transparent, showing through any "underlying" widgets.
        # By calling swapBuffers on "show" this is prevented.
        self.swapBuffers()


class Figure(BaseFigure):
    """ This is the Qt4 implementation of the figure class.
    
    A Figure represents the OpenGl context and is the root
    of the visualization tree; a Figure Wibject does not have a parent.
    
    A Figure can be created with the function vv.figure() or vv.gcf().
    """
    
    def __init__(self, parent, *args, **kwargs):
        
        # keep same documentation
        self.__doc__ = BaseFigure.__doc__
        self._widget = None
        self._widget_args = (parent, args, kwargs)
        if kwargs.get('create_widget', True):
            self.CreateWidget()
        
        # call original init AFTER we created the widget
        BaseFigure.__init__(self)
    
    def CreateWidget(self):
        """ Create the Figure's widget if necessary, and return the
        widget. """
        if self._widget is None:
            # Make sure there is a native app and the timer is started 
            # (also when embedded)
            app.Create()
            
            # create widget
            updatePosition = False
            parent, args, kwargs = self._widget_args
            if 'create_widget' in kwargs:
                updatePosition = True
                del(kwargs['create_widget'])
            self._widget = GLWidget(self, parent, *args, **kwargs)
            if updatePosition:
                self.position._Changed()
        return self._widget
    
    
    def _SetCurrent(self):
        """ Make this scene the current OpenGL context. 
        """
        if self._widget and not self._destroyed:
            self._widget.makeCurrent()
        
    def _SwapBuffers(self):
        """ Swap the memory and screen buffer such that
        what we rendered appears on the screen """
        if self._widget and not self._destroyed:
            self._widget.swapBuffers()
        
    def _SetTitle(self, title):
        """ Set the title of the figure. Note that this
        does not have to work if the Figure is uses as
        a widget in an application.
        """
        if self._widget and not self._destroyed:
            self._widget.setWindowTitle(title)

    def _SetPosition(self, x, y, w, h):
        """ Set the position of the widget. """
        if self._widget and not self._destroyed:
            self._widget.setGeometry(x, y, w, h)
    
    def _GetPosition(self):
        """ Get the position of the widget. """        
        if self._widget and not self._destroyed:
            tmp = self._widget.geometry()
            return tmp.left(), tmp.top(), tmp.width(), tmp.height()
        return 0, 0, 0, 0
    
    def _RedrawGui(self):
        if self._widget:
            self._widget.update()
    
    def _ProcessGuiEvents(self):
        app.ProcessEvents()
#         app = QtGui.QApplication.instance()
#         app.flush()
#         app.processEvents()
    
    
    def _Close(self, widget):
        if widget is None:
            widget = self._widget
        if widget:
            widget.close()


def newFigure():
    """ function that produces a new Figure object, the widget
    in a window. """
    
    # Create figure
    fig = Figure(None)
    fig._widget.show() # In Gnome better to show before resize
    size = visvis.settings.figureSize
    fig._widget.resize(size[0],size[1])
    
    # Let OpenGl initialize and return
    fig.DrawNow() 
    return fig



class App(events.App):
    """ App()
    
    Application class to wrap the GUI applications in a class
    with a simple interface that is the same for all backends.
    
    This is the Qt4 implementation.
    
    """
    
    def __init__(self):
        self._timer = None
    
    def _GetNativeApp(self):
        # Get native app in save way. Taken from guisupport.py
        app = QtGui.QApplication.instance()
        if app is None:
            app = QtGui.QApplication([''])
        # Store so it won't be deleted, but not on a visvis object,
        # or an application may produce error when closed
        QtGui._qApp = app
        # Start timer
        if self._timer is None:
            # Instantiate timer
            self._timer = QtCore.QTimer()
            self._timer.setInterval(10)
            self._timer.setSingleShot(False)
            self._timer.timeout.connect(events.processVisvisEvents)
            self._timer.start()
        # Return
        return app
    
    def _ProcessEvents(self):
        app = self._GetNativeApp()
        app.flush()
        app.processEvents()
    
    def _Run(self):
        app = self._GetNativeApp()
        if hasattr(app, '_in_event_loop') and app._in_event_loop:
            pass # Already in event loop
        else:
            app.exec_()

# Create application instance now
app = App()
