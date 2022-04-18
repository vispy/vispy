#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Abstract: show mesh primitive
# Keywords: cone, arrow, sphere, cylinder, qt
# -----------------------------------------------------------------------------

"""
Test the fps capability of Vispy with meshdata primitive
"""
try:
    from sip import setapi
    setapi("QVariant", 2)
    setapi("QString", 2)
except ImportError:
    pass


# To switch between PyQt5 and PySide2 bindings just change the from import
from PyQt5 import QtCore, QtWidgets

import sys

import numpy as np
from vispy import app, gloo
from vispy.util.transforms import perspective, translate, rotate
from vispy.geometry import meshdata as md
from vispy.geometry import generation as gen

# Provide automatic signal function selection for PyQt5/PySide2
pyqtsignal = QtCore.pyqtSignal if hasattr(QtCore, 'pyqtSignal') else QtCore.Signal


OBJECT = {'sphere': [('rows', 3, 1000, 'int', 3),
                     ('cols', 3, 1000, 'int', 3),
                     ('radius', 0.1, 10, 'double', 1.0)],
          'cylinder': [('rows', 4, 1000, 'int', 4),
                       ('cols', 4, 1000, 'int', 4),
                       ('radius', 0.1, 10, 'double', 1.0),
                       ('radius Top.', 0.1, 10, 'double', 1.0),
                       ('length', 0.1, 10, 'double', 1.0)],
          'cone': [('cols', 3, 1000, 'int', 3),
                   ('radius', 0.1, 10, 'double', 1.0),
                   ('length', 0.1, 10, 'double', 1.0)],
          'arrow': [('rows', 4, 1000, 'int', 4),
                    ('cols', 4, 1000, 'int', 4),
                    ('radius', 0.01, 10, 'double', 0.1),
                    ('length', 0.1, 10, 'double', 1.0),
                    ('cone_radius', 0.1, 10, 'double', 0.2),
                    ('cone_length', 0.0, 10., 'double', 0.3)]}

vert = """
// Uniforms
// ------------------------------------
uniform   mat4 u_model;
uniform   mat4 u_view;
uniform   mat4 u_projection;
uniform   vec4 u_color;

// Attributes
// ------------------------------------
attribute vec3 a_position;
attribute vec3 a_normal;
attribute vec4 a_color;

// Varying
// ------------------------------------
varying vec4 v_color;

void main()
{
    v_color = a_color * u_color;
    gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
}
"""


frag = """
// Varying
// ------------------------------------
varying vec4 v_color;

void main()
{
    gl_FragColor = v_color;
}
"""

DEFAULT_COLOR = (0, 1, 1, 1)
# -----------------------------------------------------------------------------


class MyMeshData(md.MeshData):
    """ Add to Meshdata class the capability to export good data for gloo """

    def __init__(self, vertices=None, faces=None, edges=None,
                 vertex_colors=None, face_colors=None):
        md.MeshData.__init__(self, vertices=None, faces=None, edges=None,
                             vertex_colors=None, face_colors=None)

    def get_glTriangles(self):
        """
        Build vertices for a colored mesh.
            V  is the vertices
            I1 is the indices for a filled mesh (use with GL_TRIANGLES)
            I2 is the indices for an outline mesh (use with GL_LINES)
        """
        vtype = [('a_position', np.float32, 3),
                 ('a_normal', np.float32, 3),
                 ('a_color', np.float32, 4)]
        vertices = self.get_vertices()
        normals = self.get_vertex_normals()
        faces = np.uint32(self.get_faces())

        edges = np.uint32(self.get_edges().reshape((-1)))
        colors = self.get_vertex_colors()

        nbrVerts = vertices.shape[0]
        V = np.zeros(nbrVerts, dtype=vtype)
        V[:]['a_position'] = vertices
        V[:]['a_normal'] = normals
        V[:]['a_color'] = colors

        return V, faces.reshape((-1)), edges.reshape((-1))
# -----------------------------------------------------------------------------


class ObjectParam(object):
    """
    OBJECT parameter test
    """

    def __init__(self, name, list_param):
        self.name = name
        self.list_param = list_param
        self.props = {}
        self.props['visible'] = True
        for nameV, minV, maxV, typeV, iniV in list_param:
            self.props[nameV] = iniV
# -----------------------------------------------------------------------------


class ObjectWidget(QtWidgets.QWidget):
    """
    Widget for editing OBJECT parameters
    """
    signal_objet_changed = pyqtsignal(ObjectParam, name='objectChanged')

    def __init__(self, parent=None, param=None):
        super(ObjectWidget, self).__init__(parent)

        if param is None:
            self.param = ObjectParam('sphere', OBJECT['sphere'])
        else:
            self.param = param

        self.gb_c = QtWidgets.QGroupBox(u"Hide/Show %s" % self.param.name)
        self.gb_c.setCheckable(True)
        self.gb_c.setChecked(self.param.props['visible'])
        self.gb_c.toggled.connect(self.update_param)

        lL = []
        self.sp = []
        gb_c_lay = QtWidgets.QGridLayout()
        for nameV, minV, maxV, typeV, iniV in self.param.list_param:
            lL.append(QtWidgets.QLabel(nameV, self.gb_c))
            if typeV == 'double':
                self.sp.append(QtWidgets.QDoubleSpinBox(self.gb_c))
                self.sp[-1].setDecimals(2)
                self.sp[-1].setSingleStep(0.1)
                self.sp[-1].setLocale(QtCore.QLocale(QtCore.QLocale.English))
            elif typeV == 'int':
                self.sp.append(QtWidgets.QSpinBox(self.gb_c))
            self.sp[-1].setMinimum(minV)
            self.sp[-1].setMaximum(maxV)
            self.sp[-1].setValue(iniV)

        # Layout
        for pos in range(len(lL)):
            gb_c_lay.addWidget(lL[pos], pos, 0)
            gb_c_lay.addWidget(self.sp[pos], pos, 1)
            # Signal
            self.sp[pos].valueChanged.connect(self.update_param)

        self.gb_c.setLayout(gb_c_lay)

        vbox = QtWidgets.QVBoxLayout()
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.gb_c)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def update_param(self, option):
        """
        update param and emit a signal
        """
        self.param.props['visible'] = self.gb_c.isChecked()
        keys = map(lambda x: x[0], self.param.list_param)
        for pos, nameV in enumerate(keys):
            self.param.props[nameV] = self.sp[pos].value()
        # emit signal
        self.signal_objet_changed.emit(self.param)
# -----------------------------------------------------------------------------


class Canvas(app.Canvas):

    def __init__(self,):
        app.Canvas.__init__(self)
        self.size = 800, 600
        # fovy, zfar params
        self.fovy = 45.0
        self.zfar = 10.0
        width, height = self.size
        self.aspect = width / float(height)

        self.program = gloo.Program(vert, frag)

        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)
        self.view = translate((0, 0, -5.0))

        self.program['u_model'] = self.model
        self.program['u_view'] = self.view

        self.theta = 0
        self.phi = 0
        self.visible = True

        self._timer = app.Timer(1.0 / 60)
        self._timer.connect(self.on_timer)
        self._timer.start()

    # ---------------------------------
        gloo.set_clear_color((1, 1, 1, 1))
        gloo.set_state('opaque')
        gloo.set_polygon_offset(1, 1)

    # ---------------------------------
    def on_timer(self, event):
        self.theta += .5
        self.phi += .5
        self.model = np.dot(rotate(self.theta, (0, 0, 1)),
                            rotate(self.phi, (0, 1, 0)))
        self.program['u_model'] = self.model
        self.update()

    # ---------------------------------
    def on_resize(self, event):
        width, height = event.size
        self.size = event.size
        gloo.set_viewport(0, 0, width, height)
        self.aspect = width / float(height)
        self.projection = perspective(self.fovy, width / float(height), 1.0,
                                      self.zfar)
        self.program['u_projection'] = self.projection

    # ---------------------------------
    def on_draw(self, event):
        gloo.clear()
        if self.visible:
            # Filled mesh
            gloo.set_state(blend=False, depth_test=True,
                           polygon_offset_fill=True)
            self.program['u_color'] = 1, 1, 1, 1
            self.program.draw('triangles', self.filled_buf)

            # Outline
            gloo.set_state(blend=True, depth_test=True,
                           polygon_offset_fill=False)
            gloo.set_depth_mask(False)
            self.program['u_color'] = 0, 0, 0, 1
            self.program.draw('lines', self.outline_buf)
            gloo.set_depth_mask(True)

    # ---------------------------------
    def set_data(self, vertices, filled, outline):
        self.filled_buf = gloo.IndexBuffer(filled)
        self.outline_buf = gloo.IndexBuffer(outline)
        self.vertices_buff = gloo.VertexBuffer(vertices)
        self.program.bind(self.vertices_buff)
        self.update()
# -----------------------------------------------------------------------------


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        self.resize(700, 500)
        self.setWindowTitle('vispy example ...')

        self.list_object = QtWidgets.QListWidget()
        self.list_object.setAlternatingRowColors(True)
        self.list_object.itemSelectionChanged.connect(self.list_objectChanged)

        self.list_object.addItems(list(OBJECT.keys()))
        self.props_widget = ObjectWidget(self)
        self.props_widget.signal_objet_changed.connect(self.update_view)

        self.splitter_v = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitter_v.addWidget(self.list_object)
        self.splitter_v.addWidget(self.props_widget)

        self.canvas = Canvas()
        self.canvas.create_native()
        self.canvas.native.setParent(self)
        self.canvas.measure_fps(0.1, self.show_fps)

        # Central Widget
        splitter1 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(self.splitter_v)
        splitter1.addWidget(self.canvas.native)

        self.setCentralWidget(splitter1)

        # FPS message in statusbar:
        self.status = self.statusBar()
        self.status_label = QtWidgets.QLabel('...')
        self.status.addWidget(self.status_label)

        self.mesh = MyMeshData()
        self.update_view(self.props_widget.param)

    def list_objectChanged(self):
        row = self.list_object.currentIndex().row()
        name = self.list_object.currentIndex().data()
        if row != -1:
            self.props_widget.deleteLater()
            self.props_widget = ObjectWidget(self, param=ObjectParam(name,
                                                                     OBJECT[name]))
            self.splitter_v.addWidget(self.props_widget)
            self.props_widget.signal_objet_changed.connect(self.update_view)
            self.update_view(self.props_widget.param)

    def show_fps(self, fps):
        nbr_tri = self.mesh.n_faces
        msg = "FPS - %0.2f and nbr Tri %s " % (float(fps), int(nbr_tri))
        # NOTE: We can't use showMessage in PyQt5 because it causes
        #       a draw event loop (show_fps for every drawing event,
        #       showMessage causes a drawing event, and so on).
        self.status_label.setText(msg)

    def update_view(self, param):
        cols = param.props['cols']
        radius = param.props['radius']
        if param.name == 'sphere':
            rows = param.props['rows']
            mesh = gen.create_sphere(cols, rows, radius=radius)
        elif param.name == 'cone':
            length = param.props['length']
            mesh = gen.create_cone(cols, radius=radius, length=length)
        elif param.name == 'cylinder':
            rows = param.props['rows']
            length = param.props['length']
            radius2 = param.props['radius Top.']
            mesh = gen.create_cylinder(rows, cols, radius=[radius, radius2],
                                       length=length)
        elif param.name == 'arrow':
            length = param.props['length']
            rows = param.props['rows']
            cone_radius = param.props['cone_radius']
            cone_length = param.props['cone_length']
            mesh = gen.create_arrow(rows, cols, radius=radius, length=length,
                                    cone_radius=cone_radius,
                                    cone_length=cone_length)
        else:
            return

        self.canvas.visible = param.props['visible']
        self.mesh.set_vertices(mesh.get_vertices())
        self.mesh.set_faces(mesh.get_faces())
        colors = np.tile(DEFAULT_COLOR, (self.mesh.n_vertices, 1))
        self.mesh.set_vertex_colors(colors)
        vertices, filled, outline = self.mesh.get_glTriangles()
        self.canvas.set_data(vertices, filled, outline)

# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':

    appQt = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    appQt.exec_()
