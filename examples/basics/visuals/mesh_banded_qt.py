# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of Mesh visual with banded capability in Qt5.
"""

# from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

import numpy as np
import sys

from PyQt4.QtGui import (QWidget, QGroupBox, QGridLayout, QLabel,
                             QSpinBox, QSplitter, QMainWindow, QAction,
                             QApplication, QVBoxLayout, QHBoxLayout,
                             qApp, QComboBox)

from PyQt4.QtCore import (pyqtSignal, Qt)

from vispy.color.colormap import get_colormaps
from vispy import scene
from vispy.geometry import create_sphere
from vispy import use

use("PyQt4")


def xyz_to_gp(xyz):
    """
    Input X, Y, Z, the Cartesian coordinates of a point
    on the unit sphere.
    Output, float gamma and phi coordinates of the point.

    phi is a longitudinal angle and gamma is a latitudinal

    x = np.sin(gamma)*np.cos(phi)
    y = np.sin(gamma)*np.sin(phi)
    z = np.cos(gamma)

    """
    x = xyz[:, 0]
    y = xyz[:, 1]
    z = xyz[:, 2]
    gamma = np.arccos(z)
    fact = np.sqrt(x*x+y*y)
    phi = np.where(fact > 0.0, np.arccos(x/fact), np.arccos(x))
    phi = np.where(y < 0.0, -phi, phi)

    return gamma, phi


class SphereParam(object):
    """
    Spehre's parameter
    """
    def __init__(self):
        self.dict = {}
        self.dict['subdiv'] = 2
        self.dict["banded"] = False
        self.dict["nbr_band"] = 10
        self.dict["colormap"] = None
        self.dict["subdiv_old"] = 0
        self.dict["data"] = None


class SphereWidget(QWidget):
    """
    Widget for editing sphere's parameters
    """

    signalObjetChanged = pyqtSignal(SphereParam, name='signal_objet_changed')

    def __init__(self, parent=None, param=None):
        super(SphereWidget, self).__init__(parent)

        if param is None:
            self.param = SphereParam()
        else:
            self.param = param

        gbC_lay = QVBoxLayout()

        l_cmap = QLabel("Cmap ")
        self.cmap = list(get_colormaps().keys())
        self.combo = QComboBox(self)
        self.combo.addItems(self.cmap)
        self.combo.currentIndexChanged.connect(self.updateParam)
        self.param.dict["colormap"] = self.cmap[0]
        hbox = QHBoxLayout()
        hbox.addWidget(l_cmap)
        hbox.addWidget(self.combo)
        gbC_lay.addLayout(hbox)

        self.sp = []
        # subdiv
        lL = QLabel("subdiv")
        self.sp.append(QSpinBox())
        self.sp[-1].setMinimum(0)
        self.sp[-1].setMaximum(6)
        self.sp[-1].setValue(self.param.dict["subdiv"])
        # Layout
        hbox = QHBoxLayout()
        hbox.addWidget(lL)
        hbox.addWidget(self.sp[-1])
        gbC_lay.addLayout(hbox)
        # signal's
        self.sp[-1].valueChanged.connect(self.updateParam)
        # Banded
        self.gbBand = QGroupBox(u"Banded")
        self.gbBand.setCheckable(True)
        hbox = QGridLayout()
        lL = QLabel("nbr band", self.gbBand)
        self.sp.append(QSpinBox(self.gbBand))
        self.sp[-1].setMinimum(0)
        self.sp[-1].setMaximum(100)
        # Layout
        hbox = QHBoxLayout()
        hbox.addWidget(lL)
        hbox.addWidget(self.sp[-1])
        self.gbBand.setLayout(hbox)
        gbC_lay.addWidget(self.gbBand)
        # signal's
        self.sp[-1].valueChanged.connect(self.updateParam)
        self.gbBand.toggled.connect(self.updateParam)

        gbC_lay.addStretch(1.0)

        hbox = QHBoxLayout()
        hbox.addLayout(gbC_lay)

        self.setLayout(hbox)
        self.updateMenu()

    def updateParam(self, option):
        """
        update param and emit a signal
        """

        tab = ["subdiv", "nbr_band"]
        for pos, name in enumerate(tab):
            self.param.dict[name] = self.sp[pos].value()
        self.param.dict["banded"] = self.gbBand.isChecked()
        self.param.dict["colormap"] = self.combo.currentText()
        # emit signal
        self.signalObjetChanged.emit(self.param)

    def updateMenu(self, param=None):
        """
        Update menus
        """
        if param is not None:
            self.param = param
        # Lock signals
        self.blockSignals(True)
        for wid in self.sp:
            wid.blockSignals(True)
        tab = ["subdiv", "nbr_band"]
        for pos, name in enumerate(tab):
            self.sp[pos].setValue(self.param.dict[name])
        self.gbBand.setChecked(self.param.dict["banded"])
        # unlock signals
        self.blockSignals(False)
        for wid in self.sp:
            wid.blockSignals(False)
        self.signalObjetChanged.emit(self.param)


class SphereCanvas(scene.SceneCanvas):

    def __init__(self, param=None):
        scene.SceneCanvas.__init__(self, keys=None)
        self.size = 800, 600
        self.unfreeze()
        grid = self.central_widget.add_grid(margin=10)
        self.view = grid.add_view(row=0, col=0, border_color='white')

        self.view.camera = 'turntable'
        self.sph = None
        cmap = "cool"
        if param is not None:
            subdiv = param.dict['subdiv']
            self.sph = scene.visuals.Sphere(radius=1, method='ico',
                                            parent=self.view.scene,
                                            subdivisions=subdiv)
            cmap = param.dict["colormap"]

        # Add a 3D axis to keep us oriented
        self.cbar_widget = scene.ColorBarWidget(label="ColorBarWidget",
                                                clim=(0, 1),
                                                cmap=cmap,
                                                orientation="right",
                                                position='right',
                                                border_width=1,
                                                parent=self.view.scene,
                                                label_color="w")
        self.cbar_widget.width_max = 100
        grid.add_widget(self.cbar_widget, row=0, col=1)
        self.freeze()

    def updateView(self, param):

        if param.dict["subdiv"] != param.dict["subdiv_old"]:
            subdiv = param.dict['subdiv']
            md = create_sphere(radius=1, subdivisions=subdiv, method='ico')
            verts = md.get_vertices()
            print(verts.shape)
            faces = md.get_faces()
            gamma, phi = xyz_to_gp(verts)
            data = np.cos(5*gamma)+np.cos(phi*4)/2.
            param.dict["data"] = data
            self.sph.mesh.set_data(vertices=verts, faces=faces,
                                   vertex_values=data)
            param.dict["subdiv_old"] = param.dict["subdiv"]

        self.sph.mesh.cmap = param.dict['colormap']
        self.cbar_widget.cmap = param.dict['colormap']
        self.cbar_widget.nband = param.dict['nbr_band']
        self.cbar_widget.banded = param.dict['banded']

        v_min = 0.0
        v_max = 1.0
        if param.dict["data"] is not None:
            v_min = np.min(param.dict["data"], 0)
            v_max = np.max(param.dict["data"], 0)
        self.cbar_widget.clim = (v_min, v_max)

        self.sph.mesh.nband = param.dict['nbr_band']
        self.sph.mesh.banded = param.dict['banded']


class SphereMainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.resize(300, 300)
        self.setWindowTitle('MeshVisual example')

        self.initActions()
        self.initMenus()

        # Central Widget
        splitter1 = QSplitter(Qt.Horizontal)

        self.propsWidget = SphereWidget()

        self.canvas = SphereCanvas(param=self.propsWidget.param)
        self.canvas.create_native()
        self.canvas.native.setParent(self)

        self.propsWidget.signalObjetChanged.connect(self.canvas.updateView)
        splitter1.addWidget(self.propsWidget)
        splitter1.addWidget(self.canvas.native)

        self.setCentralWidget(splitter1)
        self.canvas.updateView(self.propsWidget.param)

    def initActions(self):
        self.exitAction = QAction('Quit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.close)

    def initMenus(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.exitAction)

    def close(self):
        qApp.quit()


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = SphereMainWindow()
    win.show()
    sys.exit(app.exec_())
