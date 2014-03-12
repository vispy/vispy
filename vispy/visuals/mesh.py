# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .. import gloo
from .visual import Visual
from .transforms import AffineTransform
from ..shaders.composite import ModularProgram
from ..util.meshdata import MeshData

# borrow these for now.. later, we'll either customize or standardize them.
from .line import LinePosInputComponent, LineColorInputComponent

VERTEX_SHADER = """
// local_position function must return the current vertex position
// in the Visual's local coordinate system.
vec4 local_position();

// mapping function that transforms from the Visual's local coordinate
// system to normalized device coordinates.
vec4 map_local_to_nd(vec4);

// generic hook for executing code after the vertex position has been set
void vert_post_hook();

void main(void) {
    vec4 local_pos = local_position();
    vec4 nd_pos = map_local_to_nd(local_pos);
    gl_Position = nd_pos;
    
    vert_post_hook();
}
"""

FRAGMENT_SHADER = """
// Must return the color for this fragment
// or discard.
vec4 frag_color();

// Generic hook for executing code after the fragment color has been set
// Functions in this hook may modify glFragColor or discard.
void frag_post_hook();

void main(void) {
    gl_FragColor = frag_color();
    
    frag_post_hook();
}
"""



class MeshVisual(Visual):
    """
    Displays a 3D triangle mesh. 
    """
    def __init__(self, **kwds):
        """
        ==============  ========================================================
        **Arguments:**
        meshdata        MeshData object from which to determine geometry for 
                        this item.
        color           Default face color used if no vertex or face colors 
                        are specified.
        edge_color      Default edge color to use if no edge colors are
                        specified in the mesh data.
        draw_edges      If True, a wireframe mesh will be drawn. 
                        (default=False)
        draw_faces      If True, mesh faces are drawn. (default=True)
        shader          Name of shader program to use when drawing faces.
                        (None for no shader)
        smooth          If True, normal vectors are computed for each vertex
                        and interpolated within each face.
        compute_normals If False, then computation of normal vectors is 
                        disabled. This can provide a performance boost for 
                        meshes that do not make use of normals.
        ==============  ========================================================
        """
        super(MeshVisual, self).__init__()
        
        self._opts = {
            'meshdata': None,
            'color': (1., 1., 1., 1.),
            'draw_edges': False,
            'draw_faces': True,
            'edge_color': (0.5, 0.5, 0.5, 1.0),
            'smooth': True,
            'compute_normals': True,
        }
        
        self._program = ModularProgram(vertex_shader, fragment_shader)
        
        self.transform = NullTransform()
        
        # Generic chains for attaching post-processing functions
        self._program.add_chain('vert_post_hook')
        self._program.add_chain('frag_post_hook')
        
        # Components for plugging different types of position and color input.
        self._pos_input_component = None
        self._color_input_component = None
        self.pos_input_component = LinePosInputComponent(self)
        self.color_input_component = LineColorInputComponent(self)
        
        self._vbo = None
        
        glopts = kwds.pop('gl_options', 'opaque')
        self.set_gl_options(glopts)
        
        self.set_mesh_data(**kwds)
        
        ## storage for data compiled from MeshData object
        self.vertexes = None
        self.normals = None
        self.colors = None
        self.faces = None
        
    def set_color(self, c):
        """Set the default color to use when no vertex or face colors are specified."""
        self._opts['color'] = c
        self.update()
        
    def set_mesh_data(self, **kwds):
        """
        Set mesh data for this item. This can be invoked two ways:
        
        1. Specify *meshdata* argument with a new MeshData object
        2. Specify keyword arguments to be passed to MeshData(..) to create a new instance.
        """
        md = kwds.get('meshdata', None)
        if md is None:
            opts = {}
            for k in ['vertexes', 'faces', 'edges', 'vertex_colors', 'face_colors']:
                try:
                    opts[k] = kwds.pop(k)
                except KeyError:
                    pass
            md = MeshData(**opts)
        
        self._opts['meshdata'] = md
        self._opts.update(kwds)
        self.mesh_data_changed()
        self.update()
        
    
    def mesh_data_changed(self):
        """
        This method must be called to inform the item that the MeshData object
        has been altered.
        """
        
        self.vertexes = None
        self.faces = None
        self.normals = None
        self.colors = None
        self.edges = None
        self.edge_colors = None
        self.update()


    
    def parse_mesh_data(self):
        ## interpret vertex / normal data before drawing
        ## This can:
        ##   - automatically generate normals if they were not specified
        ##   - pull vertexes/noormals/faces from MeshData if that was specified
        
        if self.vertexes is not None and self.normals is not None:
            return
        #if self._opts['normals'] is None:
            #if self._opts['meshdata'] is None:
                #self._opts['meshdata'] = MeshData(vertexes=self._opts['vertexes'], faces=self._opts['faces'])
        if self._opts['meshdata'] is not None:
            md = self._opts['meshdata']
            if self._opts['smooth'] and not md.has_face_indexed_data():
                self.vertexes = md.vertexes()
                if self._opts['compute_normals']:
                    self.normals = md.vertex_normals()
                self.faces = md.faces()
                if md.has_vertex_color():
                    self.colors = md.vertex_colors()
                if md.has_face_color():
                    self.colors = md.face_colors()
            else:
                self.vertexes = md.vertexes(indexed='faces')
                if self._opts['compute_normals']:
                    if self._opts['smooth']:
                        self.normals = md.vertex_normals(indexed='faces')
                    else:
                        self.normals = md.face_normals(indexed='faces')
                self.faces = None
                if md.has_vertex_color():
                    self.colors = md.vertex_colors(indexed='faces')
                elif md.has_face_color():
                    self.colors = md.face_colors(indexed='faces')
                    
            if self._opts['draw_edges']:
                if not md.has_face_indexed_data():
                    self.edges = md.edges()
                    self.edge_verts = md.vertexes()
                else:
                    self.edges = md.edges()
                    self.edge_verts = md.vertexes(indexed='faces')
            return

    def _build_vbo(self):
        # Construct complete data array with position and optionally color
        
        pos = self._opts['pos']
        typ = [('pos', np.float32, pos.shape[-1])]
        color = self._opts['color']
        color_is_array = isinstance(color, np.ndarray) and color.ndim > 1
        if color_is_array:
            typ.append(('color', np.float32, self._opts['color'].shape[-1]))
        
        self._data = np.empty(pos.shape[:-1], typ)
        self._data['pos'] = pos
        if color_is_array:
            self._data['color'] = color

        # convert to vertex buffer
        self._vbo = gloo.VertexBuffer(self._data)


    
    def paint(self):
        
        
        if self._opts['draw_faces']:
            with self.shader():
                verts = self.vertexes
                norms = self.normals
                color = self.colors
                faces = self.faces
                if verts is None:
                    return
                glEnableClientState(GL_VERTEX_ARRAY)
                try:
                    glVertexPointerf(verts)
                    
                    if self.colors is None:
                        color = self._opts['color']
                        if isinstance(color, QtGui.QColor):
                            glColor4f(*fn.glColor(color))
                        else:
                            glColor4f(*color)
                    else:
                        glEnableClientState(GL_COLOR_ARRAY)
                        glColorPointerf(color)
                    
                    
                    if norms is not None:
                        glEnableClientState(GL_NORMAL_ARRAY)
                        glNormalPointerf(norms)
                    
                    if faces is None:
                        glDrawArrays(GL_TRIANGLES, 0, np.product(verts.shape[:-1]))
                    else:
                        faces = faces.astype(np.uint).flatten()
                        glDrawElements(GL_TRIANGLES, faces.shape[0], GL_UNSIGNED_INT, faces)
                finally:
                    glDisableClientState(GL_NORMAL_ARRAY)
                    glDisableClientState(GL_VERTEX_ARRAY)
                    glDisableClientState(GL_COLOR_ARRAY)
            
        if self._opts['draw_edges']:
            verts = self.edge_verts
            edges = self.edges
            glEnableClientState(GL_VERTEX_ARRAY)
            try:
                glVertexPointerf(verts)
                
                if self.edge_colors is None:
                    color = self._opts['edge_color']
                    if isinstance(color, QtGui.QColor):
                        glColor4f(*fn.glColor(color))
                    else:
                        glColor4f(*color)
                else:
                    glEnableClientState(GL_COLOR_ARRAY)
                    glColorPointerf(color)
                edges = edges.flatten()
                glDrawElements(GL_LINES, edges.shape[0], GL_UNSIGNED_INT, edges)
            finally:
                glDisableClientState(GL_VERTEX_ARRAY)
                glDisableClientState(GL_COLOR_ARRAY)
            
    def paint(self):
        super(PointsVisual, self).paint()
        
        if self._vbo is None:
            self._build_vbo()
            
            # tell components to use the new VBO data
            self.pos_input_component.update()
            self.color_input_component.update()
        
        # TODO: this must be optimized.
        self._program['map_local_to_nd'] = self.transform.shader_map()
        
        self._program.draw(gloo.gl.GL_TRIANGLES)


