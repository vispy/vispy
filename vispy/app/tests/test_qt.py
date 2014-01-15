# Import PyQt4, vispy will see this and use that as a backend
# Also import QtOpenGL, because vispy needs it.

# This is a strange test: vispy does not need designer or uic stuff to run!

import numpy as np
import OpenGL.GL as gl
import os

from vispy.app import Canvas

test_qt = True
try:
    from PyQt4 import QtCore, QtGui, QtOpenGL, uic
    test_uic = True
except ImportError:
    try:
        from PySide import QtCore, QtGui, QtOpenGL
    except ImportError:
        test_qt = False
    test_uic = False

requires_qt = np.testing.dec.skipif(not test_qt, 'Requires QT')
runs_uic = np.testing.dec.skipif(not test_uic, 'Not testing UIC')


@requires_qt
@runs_uic
def test_qt_designer():
    """Embed Canvas via Qt Designer"""
    app = QtGui.QApplication([])
    path = os.path.dirname(__file__)
    WindowTemplate, TemplateBaseClass = uic.loadUiType(
        os.path.join(
            path, 'qt-designer.ui'))

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
    if test_qt and test_uic:
        test_qt_designer()
