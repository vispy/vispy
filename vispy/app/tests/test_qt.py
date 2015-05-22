# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from os import path as op
import warnings

from vispy.testing import requires_application


@requires_application('pyqt4', has=['uic'])
def test_qt_designer():
    """Embed Canvas via Qt Designer"""
    from PyQt4 import QtGui, uic
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication([])
    
    fname = op.join(op.dirname(__file__), 'qt-designer.ui')
    with warnings.catch_warnings(record=True):  # pyqt4 deprecation warning
        WindowTemplate, TemplateBaseClass = uic.loadUiType(fname)

    class MainWindow(TemplateBaseClass):
        def __init__(self):
            TemplateBaseClass.__init__(self)
            
            self.ui = WindowTemplate()
            self.ui.setupUi(self)

    win = MainWindow()
    
    try:
        canvas = win.ui.canvas
        # test we can access properties of the internal canvas:
        canvas.central_widget.add_view()
        win.show()
        app.processEvents()
    finally:
        win.close()
    
    return win


# Don't use run_tests_if_main(), because we want to show the win
if __name__ == '__main__':
    win = test_qt_designer()
    win.show()
