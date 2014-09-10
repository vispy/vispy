# Import PyQt4, vispy will see this and use that as a backend
# Also import QtOpenGL, because vispy needs it.

# This is a strange test: vispy does not need designer or uic stuff to run!

from os import path as op
import warnings

from vispy.app import Canvas, use_app

from vispy.testing import requires_application, SkipTest
from vispy import gloo


@requires_application('pyqt4', has=['uic'])
def test_qt_designer():
    """Embed Canvas via Qt Designer"""
    app = use_app()
    if 'pyqt4' not in app.backend_name.lower():
        raise SkipTest('Not using PyQt4 backend')  # wrong backend
    from PyQt4 import uic
    fname = op.join(op.dirname(__file__), 'qt-designer.ui')
    with warnings.catch_warnings(record=True):  # pyqt4 deprecation warning
        WindowTemplate, TemplateBaseClass = uic.loadUiType(fname)
    app.create()  # make sure we have an app, or the init will fail

    class MainWindow(TemplateBaseClass):
        def __init__(self):
            TemplateBaseClass.__init__(self)
            
            self.ui = WindowTemplate()
            self.ui.setupUi(self)

    win = MainWindow()
    
    try:
        win.show()
        canvas = Canvas(parent=win.ui.canvas_placeholder)
        canvas.native.embed(win.ui.canvas_placeholder)

        @canvas.events.draw.connect
        def on_draw(ev):
            gloo.clear('g')
            canvas.swap_buffers()
    finally:
        win.close()
    
    return win


# Don't use run_tests_if_main(), because we want to show the win
if __name__ == '__main__':
    win = test_qt_designer()
    win.show()
