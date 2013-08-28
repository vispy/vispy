# Import PyQt4, vispy will see this and use that as a backend
# Also import QtOpenGL, because vispy needs it.
from PyQt4 import QtCore, QtGui, QtOpenGL, uic

import OpenGL.GL as gl
from vispy.app import Canvas
import os


path = os.path.dirname(__file__)
WindowTemplate, TemplateBaseClass = uic.loadUiType(os.path.join(path, 'qt-designer.ui'))

class MainWindow(TemplateBaseClass):  
    def __init__(self):
        TemplateBaseClass.__init__(self)
        
        self.ui = WindowTemplate()
        self.ui.setupUi(self)
        self.show()
        
app = QtGui.QApplication([])
        
def test_qt_designer():
    """Embed Canvas via Qt Designer"""
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
