# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""
This example demonstrates isocurve for triangular mesh with vertex data and a
 qt interface.
"""

import sys
import numpy as np

from vispy import scene

from vispy.geometry.generation import create_sphere
from vispy.color.colormap import get_colormaps

try:
    from sip import setapi
    setapi("QVariant", 2)
    setapi("QString", 2)
except ImportError:
    pass

from PyQt4 import QtGui, QtCore


class ObjectWidget(QtGui.QWidget):
    """
    Widget for editing OBJECT parameters
    """
    signal_objet_changed = QtCore.pyqtSignal(name='objectChanged')

    def __init__(self, parent=None):
        super(ObjectWidget, self).__init__(parent)

        l_nbr_steps = QtGui.QLabel("Nbr Steps ")
        self.nbr_steps = QtGui.QSpinBox()
        self.nbr_steps.setMinimum(3)
        self.nbr_steps.setMaximum(100)
        self.nbr_steps.setValue(6)
        self.nbr_steps.valueChanged.connect(self.update_param)

        l_cmap = QtGui.QLabel("Cmap ")
        self.cmap = list(get_colormaps().keys())
        self.combo = QtGui.QComboBox(self)
        self.combo.addItems(self.cmap)
        self.combo.currentIndexChanged.connect(self.update_param)

        gbox = QtGui.QGridLayout()
        gbox.addWidget(l_cmap, 0, 0)
        gbox.addWidget(self.combo, 0, 1)
        gbox.addWidget(l_nbr_steps, 1, 0)
        gbox.addWidget(self.nbr_steps, 1, 1)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(gbox)
        vbox.addStretch(1.0)

        self.setLayout(vbox)

    def update_param(self, option):
        self.signal_objet_changed.emit()


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(700, 500)
        self.setWindowTitle('vispy example ...')

        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)

        self.canvas = Canvas()
        self.canvas.create_native()
        self.canvas.native.setParent(self)

        self.props = ObjectWidget()
        splitter.addWidget(self.props)
        splitter.addWidget(self.canvas.native)

        self.setCentralWidget(splitter)
        self.props.signal_objet_changed.connect(self.update_view)
        self.update_view()

    def update_view(self):
        # banded, nbr_steps, cmap
        self.canvas.set_data(self.props.nbr_steps.value(),
                             self.props.combo.currentText())


class Canvas(scene.SceneCanvas):

    def __init__(self):
        scene.SceneCanvas.__init__(self, keys=None)
        self.size = 800, 600
        self.unfreeze()
        self.view = self.central_widget.add_view()
        self.radius = 2.0
        self.view.camera = 'turntable'
        mesh = create_sphere(20, 20, radius=self.radius)
        vertices = mesh.get_vertices()
        tris = mesh.get_faces()

        cl = np.linspace(-self.radius, self.radius, 6 + 2)[1:-1]

        self.iso = scene.visuals.Isoline(vertices=vertices, tris=tris,
                                         data=vertices[:, 2],
                                         levels=cl, color_lev='autumn',
                                         parent=self.view.scene)
        self.freeze()

        # Add a 3D axis to keep us oriented
        scene.visuals.XYZAxis(parent=self.view.scene)

    def set_data(self, n_levels, cmap):
        self.iso.set_color(cmap)
        cl = np.linspace(-self.radius, self.radius, n_levels + 2)[1:-1]
        self.iso.levels = cl


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    appQt = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    appQt.exec_()
