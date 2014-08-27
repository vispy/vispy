# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

""" A Mesh Visual that uses the new shader Function.
"""

from __future__ import division

import numpy as np

from .visual import Visual
from ..shaders import ModularProgram, Function, Varying
from ...gloo import VertexBuffer, IndexBuffer, set_state
from ...geometry import MeshData
from ...color import Color

## Snippet templates (defined as string to force user to create fresh Function)
# Consider these stored in a central location in vispy ...


vertex_template = """

void main() {
   gl_Position = $transform($position);
}
"""

fragment_template = """
void main() {
  gl_FragColor = $color;
}
"""

phong_template = """
vec4 phong_shading(vec4 color) {
    vec4 o = $transform(vec4(0, 0, 0, 1));
    vec4 n = $transform(vec4($normal, 1));
    vec3 norm = normalize((n-o).xyz);
    vec3 light = normalize($light_dir.xyz);
    float p = dot(light, norm);
    p = (p < 0. ? 0. : p);
    vec4 diffuse = $light_color * p;
    diffuse.a = 1.0;
    p = dot(reflect(light, norm), vec3(0,0,1));
    if (p < 0.0) {
        p = 0.0;
    }
    vec4 specular = $light_color * 5.0 * pow(p, 100.);
    return color * ($ambient + diffuse) + specular;
}
"""

## Functions that can be used as is (don't have template variables)
# Consider these stored in a central location in vispy ...

vec3to4 = Function("""
vec4 vec3to4(vec3 xyz) {
    return vec4(xyz, 1.0);
}
""")

vec2to4 = Function("""
vec4 vec2to4(vec2 xyz) {
    return vec4(xyz, 0.0, 1.0);
}
""")


class Mesh(Visual):

    def __init__(self, vertices=None, faces=None, vertex_colors=None,
                 face_colors=None, color=(0.5, 0.5, 1, 1), meshdata=None,
                 shading=None, mode='triangles', **kwds):
        Visual.__init__(self, **kwds)
        # Create a program
        self._program = ModularProgram(vertex_template, fragment_template)

        # Define buffers
        self._vertices = VertexBuffer(np.zeros((0, 3), dtype=np.float32))
        self._normals = None
        self._faces = IndexBuffer()
        self._colors = VertexBuffer(np.zeros((0, 4), dtype=np.float32))
        self._normals = VertexBuffer(np.zeros((0, 3), dtype=np.float32))

        # Whether to use _faces index
        self._indexed = None

        # Uniform color
        self._color = Color(color).rgba

        # primtive mode
        self._mode = mode

        # varyings
        self._color_var = Varying('v_color', dtype='vec4')
        self._normal_var = Varying('v_normal', dtype='vec3')

        # Function for computing phong shading
        self._phong = None

        # Init
        self.shading = shading
        # Note we do not call subclass set_data -- often the signatures
        # do no match.
        Mesh.set_data(self, vertices=vertices, faces=faces,
                      vertex_colors=vertex_colors,
                      face_colors=face_colors, meshdata=meshdata)

    def set_data(self, vertices=None, faces=None, vertex_colors=None,
                 face_colors=None, meshdata=None, color=None):
        if meshdata is not None:
            self._meshdata = meshdata
        else:
            self._meshdata = MeshData(vertices=vertices, faces=faces,
                                      vertex_colors=vertex_colors,
                                      face_colors=face_colors)
        if color is not None:
            self._color = Color(color).rgba
        self.mesh_data_changed()

    def mesh_data_changed(self):
        self._data_changed = True
        self.update()

    def _update_data(self):
        md = self._meshdata

        # Update vertex/index buffers
        if self.shading == 'smooth' and not md.has_face_indexed_data():
            v = md.vertices()
            self._vertices.set_data(v, convert=True)
            self._normals.set_data(md.vertex_normals(), convert=True)
            self._faces.set_data(md.faces(), convert=True)
            self._indexed = True
            if md.has_vertex_color():
                self._colors.set_data(md.vertex_colors(), convert=True)
            elif md.has_face_color():
                self._colors.set_data(md.face_colors(), convert=True)
            else:
                self._colors.set_data(np.zeros((0, 4), dtype=np.float32))
        else:
            v = md.vertices(indexed='faces')
            self._vertices.set_data(v, convert=True)
            if self.shading == 'smooth':
                normals = md.vertex_normals(indexed='faces')
                self._normals.set_data(normals, convert=True)
            elif self.shading == 'flat':
                normals = md.face_normals(indexed='faces')
                self._normals.set_data(normals, convert=True)
            else:
                self._normals.set_data(np.zeros((0, 3), dtype=np.float32))
            self._indexed = False
            if md.has_vertex_color():
                self._colors.set_data(md.vertex_colors(indexed='faces'), 
                                      convert=True)
            elif md.has_face_color():
                self._colors.set_data(md.face_colors(indexed='faces'), 
                                      convert=True)
            else:
                self._colors.set_data(np.zeros((0, 4), dtype=np.float32))

        # Position input handling
        if v.shape[-1] == 2:
            self._program.vert['position'] = vec2to4(self._vertices)
        elif v.shape[-1] == 3:
            self._program.vert['position'] = vec3to4(self._vertices)
        else:
            raise TypeError("Vertex data must have shape (...,2) or (...,3).")

        # Color input handling
        colors = self._colors if self._colors.size > 0 else self._color
        self._program.vert[self._color_var] = colors

        # Shading
        if self.shading is None:
            self._program.frag['color'] = self._color_var
            self._phong = None
        else:
            self._phong = Function(phong_template)

            # Normal data comes via vertex shader
            if self._normals.size > 0:
                normals = self._normals
            else:
                normals = (1., 0., 0.)

            self._program.vert[self._normal_var] = normals
            self._phong['normal'] = self._normal_var

            # Additional phong proprties
            self._phong['light_dir'] = (1.0, 1.0, 5.0)
            self._phong['light_color'] = (1.0, 1.0, 1.0, 1.0)
            self._phong['ambient'] = (0.3, 0.3, 0.3, 1.0)

            self._program.frag['color'] = self._phong(self._color_var)

    @property
    def shading(self):
        """ The shading method used.
        """
        return self._shading

    @shading.setter
    def shading(self, value):
        assert value in (None, 'flat', 'smooth')
        self._shading = value

    def draw(self, event):
        set_state('translucent', depth_test=True, cull_face='front_and_back')
        if self._data_changed:
            self._update_data()

        self._program.vert['transform'] = event.render_transform.shader_map()
        if self._phong is not None:
            self._phong['transform'] = event.document_transform().shader_map()

        # Draw
        if self._indexed:
            self._program.draw(self._mode, self._faces)
        else:
            self._program.draw(self._mode)
