#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test the capability of Vispy to visualize contour line on a mesh
with nodal data

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
                     ('radius', 0.1, 10, 'double', 1.0)]}

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

DEFAULT_COLOR = [0, 0.8, 1, 1]


def floatColor(mag, cmin, cmax, trans=1.0):
    """ mag is a scalar or an array with Nmag element
    Return an array (Nmag, 4) of floats between 0 and 1 for the red, green,
    blue amplitudes and transparency. """
    mag = np.array(mag)
    try:
        shape = mag.shape[0]
    except:
        shape = 1
    colors = np.zeros((shape, 4))
    try:
        # normalize to [0,1]
        x = (mag-cmin)/float(cmax-cmin)
    except:
        # cmax = cmin
        x = 0.5 + np.zeros(shape)
    # Blue
    colors[: ,0] = np.minimum(np.maximum(4*(0.75-x), 0.), 1.)
    # Red
    colors[:, 1] = np.minimum(np.maximum(4*(x-0.25), 0.), 1.)
    # Green
    colors[:, 2] = np.minimum(np.maximum(4*np.abs(x-0.5)-1., 0.), 1.)
    # Trans
    colors[:, 3] = trans
    
    return colors


def contourLine(vertices=None, faces=None, vertex_data=None, cl=None):
    """ 
    Function for calculate contour line on a triangular Mesh surface with vertex
    data.
    
    Parameters
    ----------
    vertices : ndarray, shape (Nv, 3) Vertex coordinates. 
    faces : ndarray, shape (Nf, 3) Indices into the vertex array.
    vertex_data : ndarray, shape (Nv) Vertex datas. 
    cl : ndarray, shape (Ncl) Values for isoline

    Return :
    --------
    A dict for the moment but i work on different solution

    Notes
    -----

    It's based on the hypothesis that the vertex data have a linear variation
    in the triangular face.

    The Edges vertices are not unique for the moment.

    """
    if ((cl is None or vertices is None or faces is None or
         vertex_data is None)):
        return None

    cl = np.array(cl)
    datas = vertex_data[faces]
    fmin = datas.min(axis=1)
    fmax = datas.max(axis=1)
    edgeCs = {}
    nbrEdge = 0
    for C in cl:
        pos = 0
        color = floatColor(C, cl.min(), cl.max())
        edgeCs[C] = {'index': [], 'vertices': [], 'color': color}
        # Select triangles with C between fmin and fmax
        criterion = (fmin <= C) & (C <= fmax)
        faceOKs = faces[criterion]
        for face in faceOKs:
            edges = np.vstack((face, np.roll(face, 1))).T
            edgeDatas = vertex_data[edges]
            emin = edgeDatas.min(axis=1)
            emax = edgeDatas.max(axis=1)
            # Select edge in the triangle with C betwin emin and emax
            criterion = (emin <= C) & (C <= emax)
            edges = edges[criterion]
            edgeDatas = edgeDatas[criterion]
            if edges.shape[0] >= 2:
                # if the 3 node of tringale have the C value skip the
                # the triangle
                if not np.all(vertex_data[face] == C):
                    xyz = vertices[edges]
                    if edgeDatas[0][0] == edgeDatas[0][1]:
                        edgeCs[C]['vertices'].append(xyz[0][0, :])
                        edgeCs[C]['vertices'].append(xyz[0][1, :])                        
                    elif edgeDatas[1][0] == edgeDatas[1][1]:
                        edgeCs[C]['vertices'].append(xyz[1][0, :])
                        edgeCs[C]['vertices'].append(xyz[1][1, :])                          
                    else:       
                        for i in [0, 1]:
                            ratio = (C-edgeDatas[i][0])/(edgeDatas[i][1]-edgeDatas[i][0])
                            point = xyz[i][0, :] + ratio*(xyz[i][1, :] - xyz[i][0, :])
                            edgeCs[C]['vertices'].append(point)
                    edgeCs[C]['index'].append((pos, pos+1))
                    pos = pos + 2
                    nbrEdge = nbrEdge + 1
            else:
                raise Exception("Invalid edge contouring")
    return edgeCs, nbrEdge


def test_contourLine(nbrC=2):

    vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=np.float)
    faces = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint)
    datas = np.array([0, 0, 10, 10], dtype=np.float)

    cl = np.linspace(datas.min(), datas.max(), nbrC+2)[1:-1]
    contourDict, nbrEdge = contourLine(vertices=vertices, faces=faces, vertex_data=datas, cl=cl)



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
        self.props['nbrC'] = 2
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

        gbC_lay = QtGui.QGridLayout()

        label = QtGui.QLabel(u"Nbr Cont.")
        self.spNbrC = QtGui.QSpinBox(self)
        self.spNbrC.setMaximum(20)
        self.spNbrC.setMinimum(2)
        self.spNbrC.setValue(2)
        self.spNbrC.valueChanged.connect(self.updateParam)

        self.gbC = QtGui.QGroupBox(u"Hide/Show %s" % self.param.name)
        self.gbC.setCheckable(True)
        self.gbC.setChecked(self.param.props['visible'])
        self.gbC.toggled.connect(self.updateParam)

        lL = []
        self.sp = []
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
        vbox.addWidget(label)
        vbox.addWidget(self.spNbrC)
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
        self.param.props['nbrC'] = self.spNbrC.value()
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
            self.program['u_color'] = 1, 1, 1, 1
            self.program.draw('lines', self.outline_buf)
            gloo.set_depth_mask(True)

            

    # ---------------------------------
    def set_data(self, vertices, filled, outline, diam, contourDict, nbrEdge):
        self.filled_buf = gloo.IndexBuffer(filled)
        # add contour line vertices, colors and edges
        #nbrOutline =outline.shape[0]
        nbrVertsMesh = vertices['a_position'].shape[0]
        allEdges = np.zeros(nbrEdge*2, dtype=np.uint)
        posEdge = 0
        vtype = [('a_position', np.float32, 3),
                 ('a_normal', np.float32, 3),
                 ('a_color', np.float32, 4)]
        V = np.zeros(nbrEdge*2+nbrVertsMesh, dtype=vtype)   
        posVert = nbrVertsMesh

        V[:nbrVertsMesh]['a_position'] = vertices['a_position']
        V[:nbrVertsMesh]['a_normal'] = vertices['a_normal']
        V[:nbrVertsMesh]['a_color'] = vertices['a_color']

        for C, value in contourDict.iteritems():
            color = value['color']
            index = np.array(value['index']).reshape((-1)) + posVert
            nbrIndex = index.shape[0]
            allEdges[posEdge:posEdge+nbrIndex] = index
            posEdge += nbrIndex            
            
            verts = np.array(value['vertices'])
            nbrVerts = verts.shape[0]
            V[posVert:posVert+nbrVerts]['a_position'] = verts
            V[posVert:posVert+nbrVerts]['a_normal'] = [0, 0, 0]
            V[posVert:posVert+nbrVerts]['a_color'] = color
            posVert += nbrVerts
                        
        self.outline_buf = gloo.IndexBuffer(allEdges)
        self.vertices_buff = gloo.VertexBuffer(V)
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

        self.propsWidget = ObjectWidget(self)
        self.propsWidget.signalObjetChanged.connect(self.updateView)

        self.canvas = Canvas()
        self.canvas.create_native()
        self.canvas.native.setParent(self)
        self.canvas.measure_fps(0.1, self.show_fps)

        # Central Widget
        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(self.propsWidget)
        splitter1.addWidget(self.canvas.native)

        self.setCentralWidget(splitter1)

        # FPS message in statusbar:
        self.status = self.statusBar()
        self.status.showMessage("...")

        self.mesh = MyMeshData()
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
        nbrC = param.props['nbrC']
        #Characteristc length of the mesh
        diam = radius * 2.0
        rows = param.props['rows']
        mesh = md.sphere(cols, rows, radius=radius)
        vertices = mesh.vertices()
        faces = mesh.faces()

        cl = np.linspace(-radius, radius, nbrC+2)[1:-1]
        contourDict, nbrEdge = contourLine(vertices=vertices, faces=faces, vertex_data=vertices[:, 2], cl=cl)

        self.canvas.visible = param.props['visible']
        self.mesh.set_vertices(vertices)
        self.mesh.set_faces(faces)
        self.mesh.set_vertex_colors(DEFAULT_COLOR)
        vertices, filled, outline = self.mesh.getGLTriangles()
        self.canvas.set_data(vertices, filled, outline, diam, contourDict, nbrEdge)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':

#    test_contourLine()

    appQt = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(appQt.exec_())
