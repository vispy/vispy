#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 20

"""
Example demonstrating simulation of fireworks using point sprites.
(adapted from the "OpenGL ES 2.0 Programming Guide")

This example demonstrates a series of explosions that last one second. The
visualization during the explosion is highly optimized using a Vertex Buffer
Object (VBO). After each explosion, vertex data for the next explosion are
calculated, such that each explostion is unique.
"""
# !/usr/bin/env python
# used with examples from https://github.com/vispy

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
