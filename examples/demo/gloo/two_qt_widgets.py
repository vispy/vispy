#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: testskip

"""
Example demonstrating the use of two GLCanvases in one QtApp.
"""

from PyQt4 import QtGui, QtCore
import sys

from fireworks import Canvas as FireCanvas
from rain import Canvas as RainCanvas


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(1000, 500)
        self.setWindowTitle('vispy example ...')

        self.splitter_h = QtGui.QSplitter(QtCore.Qt.Horizontal)

        # Central Widget
        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)

        self.rain_canvas = RainCanvas()
        self.rain_canvas.create_native()
        self.rain_canvas.native.setParent(self)
        self.fireworks_canvas = FireCanvas()
        self.fireworks_canvas.create_native()
        self.fireworks_canvas.native.setParent(self)

        splitter1.addWidget(self.fireworks_canvas.native)
        splitter1.addWidget(self.rain_canvas.native)

        self.setCentralWidget(splitter1)


if __name__ == '__main__':
    appQt = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    appQt.exec_()
