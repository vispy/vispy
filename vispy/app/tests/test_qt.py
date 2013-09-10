# Import PyQt4, vispy will see this and use that as a backend
# Also import QtOpenGL, because vispy needs it.

# This is a strange test: vispy does not need designer or uic stuff to run!


try:
    from PyQt4 import QtCore, QtGui, QtOpenGL, uic
    test_uic = True
except ImportError:
    from PySide import QtCore, QtGui, QtOpenGL
    test_uic = False


import OpenGL.GL as gl
from vispy.app import Canvas
import os


app = QtGui.QApplication([])

def test_qt_designer():
    """Embed Canvas via Qt Designer"""
    
    if not test_uic:
        return
    
    path = os.path.dirname(__file__)
    WindowTemplate, TemplateBaseClass = uic.loadUiType(os.path.join(path, 'qt-designer.ui'))
    
    class MainWindow(TemplateBaseClass):  
        def __init__(self):
            TemplateBaseClass.__init__(self)
            
            self.ui = WindowTemplate()
            self.ui.setupUi(self)
            self.show()
    
    global win
    win = MainWindow()
    win.show()
    canvas = Canvas(native=win.ui.canvas)
    
    @canvas.events.paint.connect
    def on_paint(ev):
        gl.glClearColor(0.0, 0.0, 0.0, 0.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        canvas.swap_buffers()



if __name__ == '__main__':
    test_qt_designer()
