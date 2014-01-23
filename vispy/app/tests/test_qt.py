# Import PyQt4, vispy will see this and use that as a backend
# Also import QtOpenGL, because vispy needs it.

# This is a strange test: vispy does not need designer or uic stuff to run!

import os
import numpy as np
import OpenGL.GL as gl

from vispy.app import Canvas
from vispy.app.backends import has_qt


requires_qt_and_uic = np.testing.dec.skipif(not has_qt(require_uic=True),
                                            'Requires Qt w/UIC')


@requires_qt_and_uic
def test_qt_designer():
    """Embed Canvas via Qt Designer"""
    from PyQt4 import QtGui, uic
    app = QtGui.QApplication([])  # noqa
    fname = os.path.join(os.path.dirname(__file__), 'qt-designer.ui')
    WindowTemplate, TemplateBaseClass = uic.loadUiType(fname)

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
    if has_qt(require_uic=True):
        test_qt_designer()
