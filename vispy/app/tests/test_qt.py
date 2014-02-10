# Import PyQt4, vispy will see this and use that as a backend
# Also import QtOpenGL, because vispy needs it.

# This is a strange test: vispy does not need designer or uic stuff to run!

from os import path as op
import OpenGL.GL as gl

from vispy.app import Canvas
from vispy.app.backends import requires_qt


@requires_qt(requires_uic=True)
def test_qt_designer():
    """Embed Canvas via Qt Designer"""
    from PyQt4 import QtGui, uic
    if not QtGui.QApplication.instance():
        QtGui.QApplication([])  # noqa
    fname = op.join(op.dirname(__file__), 'qt-designer.ui')
    WindowTemplate, TemplateBaseClass = uic.loadUiType(fname)

    class MainWindow(TemplateBaseClass):

        def __init__(self):
            TemplateBaseClass.__init__(self)

            self.ui = WindowTemplate()
            self.ui.setupUi(self)
            self.show()

    win = MainWindow()
    try:
        win.show()
        canvas = Canvas(create_native=False)
        canvas._set_backend(win.ui.canvas)
        canvas.create_native()

        @canvas.events.paint.connect
        def on_paint(ev):
            gl.glClearColor(0.0, 0.0, 0.0, 0.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            canvas.swap_buffers()
    finally:
        win.close()
