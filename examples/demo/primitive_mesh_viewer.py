#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test the fps capability of Vispy with meshdata primitive

S. Moyne le 09/07/14
"""

try:
    from sip import setapi
    setapi("QDate", 2)
    setapi("QDateTime", 2)
    setapi("QTextStream", 2)
    setapi("QTime", 2)
    setapi("QVariant", 2)
    setapi("QString", 2)
    setapi("QUrl", 2)
except:
    pass

from PyQt4 import QtGui, QtCore
import sys

import numpy as np
from vispy import app, gloo
from vispy.util.transforms import perspective, translate, rotate
from vispy.util import meshdata as md

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
                    ('fRC', 0.1, 10, 'double', 2.0),
                    ('fLC', 0.0, 1.0, 'double', 0.3)]}

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

DEFAULT_COLOR = [0, 1, 1, 1]
# -----------------------------------------------------------------------------


class MyMeshData(md.MeshData):
    """ Add to Meshdata class the capability to export good data for gloo """
    def __init__(self, vertices=None, faces=None, edges=None,
                 vertex_colors=None, face_colors=None):
        md.MeshData.__init__(self, vertices=None, faces=None, edges=None,
                             vertex_colors=None, face_colors=None)

    def getGLTriangles(self):
        """
        Build vertices for a colored mesh.
            V  is the vertices
            I1 is the indices for a filled cube (use with GL_TRIANGLES)
            I2 is the indices for an outline cube (use with GL_LINES)
        """
        vtype = [('a_position', np.float32, 3),
                 ('a_normal', np.float32, 3),
                 ('a_color', np.float32, 4)]
        vertices = self.vertices()
        normals = self.vertex_normals()
        faces = np.uint32(self.faces())

        edges = np.uint32(self.edges().reshape((-1)))
        colors = self.vertex_colors()

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
    def __init__(self, name, listParam):
        self.name = name
        self.listParam = listParam
        self.props = {}
        self.props['visible'] = True
        for nameV, minV, maxV, typeV, iniV in listParam:
            self.props[nameV] = iniV
# -----------------------------------------------------------------------------


class ObjectWidget(QtGui.QWidget):
    """
    Widget for editing OBJECT parameters
    """
    signalObjetChanged = QtCore.pyqtSignal(ObjectParam, name='objectChanged')

    def __init__(self, parent=None, param=None):
        super(ObjectWidget, self).__init__(parent)

        if param is None:
            self.param = ObjectParam('sphere', OBJECT['sphere'])
        else:
            self.param = param

        self.gbC = QtGui.QGroupBox(u"Hide/Show %s" % self.param.name)
        self.gbC.setCheckable(True)
        self.gbC.setChecked(self.param.props['visible'])
        self.gbC.toggled.connect(self.updateParam)

        lL = []
        self.sp = []
        gbC_lay = QtGui.QGridLayout()
        for nameV, minV, maxV, typeV, iniV in self.param.listParam:
            lL.append(QtGui.QLabel(nameV, self.gbC))
            if typeV == 'double':
                self.sp.append(QtGui.QDoubleSpinBox(self.gbC))
                self.sp[-1].setDecimals(2)
                self.sp[-1].setLocale(QtCore.QLocale(QtCore.QLocale.English))
            elif typeV == 'int':
                self.sp.append(QtGui.QSpinBox(self.gbC))
            self.sp[-1].setMinimum(minV)
            self.sp[-1].setMaximum(maxV)
            self.sp[-1].setValue(iniV)

        #Layout
        for pos in range(len(lL)):
            gbC_lay.addWidget(lL[pos], pos, 0)
            gbC_lay.addWidget(self.sp[pos], pos, 1)
            # Les signaux
            self.sp[pos].valueChanged.connect(self.updateParam)

        self.gbC.setLayout(gbC_lay)

        vbox = QtGui.QVBoxLayout()
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.gbC)
        hbox.addStretch(1.0)

        vbox.addLayout(hbox)
        vbox.addStretch(1.0)

        self.setLayout(vbox)

    def updateParam(self, option):
        """
        update param and emit a signal
        """
        self.param.props['visible'] = self.gbC.isChecked()
        keys = map(lambda x: x[0], self.param.listParam)
        for pos, nameV in enumerate(keys):
            self.param.props[nameV] = self.sp[pos].value()
        # emit signal
        self.signalObjetChanged.emit(self.param)

# -----------------------------------------------------------------------------


class Canvas(app.Canvas):

    def __init__(self,):
        app.Canvas.__init__(self, close_keys='escape')
        self.size = 800, 600
        #fovy, zfar params
        self.fovy = 45.0
        self.zfar = 10.0
        width, height = self.size
        self.aspect = width / float(height)

        self.program = gloo.Program(vert, frag)

        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)
        translate(self.view, 0, 0, -5.0)

        self.program['u_model'] = self.model
        self.program['u_view'] = self.view

        self.theta = 0
        self.phi = 0
        self.visible = True

        self._timer = app.Timer(1.0 / 60)
        self._timer.connect(self.on_timer)
        self._timer.start()

    # ---------------------------------
    def on_initialize(self, event):
        gloo.set_clear_color((1, 1, 1, 1))
        gloo.set_state('opaque')
        gloo.set_polygon_offset(1, 1)
        # gl.glEnable( gl.GL_LINE_SMOOTH )

    # ---------------------------------
    def on_timer(self, event):
        self.theta += .5
        self.phi += .5
        self.model = np.eye(4, dtype=np.float32)
        rotate(self.model, self.theta, 0, 0, 1)
        rotate(self.model, self.phi, 0, 1, 0)
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
            # Filled cube
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
    def set_data(self, vertices, filled, outline, diam):
        self.filled_buf = gloo.IndexBuffer(filled)
        self.outline_buf = gloo.IndexBuffer(outline)
        self.vertices_buff = gloo.VertexBuffer(vertices)
        self.program.bind(self.vertices_buff)
        #
        # FIXME: this change doesn't work
        #
        self.view = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)
        translate(self.view, 0, 0, -5.0-diam)
        self.program['u_view'] = self.view
        self.zfar = 100.0
        self.projection = perspective(self.fovy, self.aspect, 1.0, self.zfar)
        self.program['u_projection'] = self.projection
        self.update()

# -----------------------------------------------------------------------------


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(300, 300)
        self.setWindowTitle('vispy example ...')

        self.initActions()
        self.initMenus()

        self.listObject = QtGui.QListWidget()
        self.listObject.setAlternatingRowColors(True)
        self.listObject.itemSelectionChanged.connect(self.listObjectChanged)

        self.listObject.addItems(OBJECT.keys())
        #self.listObject.s
        self.propsWidget = ObjectWidget(self)
        self.propsWidget.signalObjetChanged.connect(self.updateView)

        self.splitterV = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitterV.addWidget(self.listObject)
        self.splitterV.addWidget(self.propsWidget)

        self.canvas = Canvas()
        self.canvas.create_native()
        self.canvas.native.setParent(self)
        self.canvas.measure_fps(0.1, self.show_fps)

        # Central Widget
        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(self.splitterV)
        splitter1.addWidget(self.canvas.native)

        self.setCentralWidget(splitter1)

        # FPS message in statusbar:
        self.status = self.statusBar()
        self.status.showMessage("...")

        self.mesh = MyMeshData()
        self.updateView(self.propsWidget.param)

    def listObjectChanged(self):
        row = self.listObject.currentIndex().row()
        name = self.listObject.currentIndex().data()
        if row != -1:
            self.propsWidget.deleteLater()
            self.propsWidget = ObjectWidget(self,
                                            param=ObjectParam(name,
                                                              OBJECT[name]))
            self.splitterV.addWidget(self.propsWidget)
            self.propsWidget.signalObjetChanged.connect(self.updateView)
            self.updateView(self.propsWidget.param)

    def initActions(self):
        self.exitAction = QtGui.QAction('Quit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.close)

    def initMenus(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.exitAction)

    def close(self):
        QtGui.qApp.quit()

    def show_fps(self, fps):
        nbrTri = self.mesh.face_count()
        self.status.showMessage("FPS - %.2f and nbr Tri %s " % (fps, nbrTri))

    def updateView(self, param):
        cols = param.props['cols']
        radius = param.props['radius']
        #Characteristc length of the mesh
        diam = radius * 2.0
        if param.name == 'sphere':
            rows = param.props['rows']
            mesh = md.sphere(cols, rows, radius=radius)
        elif param.name == 'cone':
            length = param.props['length']
            mesh = md.cone(cols, radius=radius, length=length)
            diam = max(diam, length*2.0)
        elif param.name == 'cylinder':
            rows = param.props['rows']
            length = param.props['length']
            radius2 = param.props['radius Top.']
            mesh = md.cylinder(rows, cols, radius=[radius, radius2],
                               length=length)
            diam = max(diam, length*2.0, radius2*2.0)
        elif param.name == 'arrow':
            length = param.props['length']
            rows = param.props['rows']
            fRC = param.props['fRC']
            fLC = param.props['fLC']
            mesh = md.arrow(rows, cols, radius=radius, length=length,
                            fRC=fRC, fLC=fLC)
            diam = max(diam, length*2.0, radius*2.0*fRC)
        else:
            return

        self.canvas.visible = param.props['visible']
        self.mesh.set_vertices(mesh.vertices())
        self.mesh.set_faces(mesh.faces())
        self.mesh.set_vertex_colors(DEFAULT_COLOR)
        vertices, filled, outline = self.mesh.getGLTriangles()
        self.canvas.set_data(vertices, filled, outline, diam)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':

    appQt = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(appQt.exec_())
