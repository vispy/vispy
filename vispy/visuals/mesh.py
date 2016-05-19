# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

""" A MeshVisual Visual that uses the new shader Function.
"""

from __future__ import division

import numpy as np

from .visual import Visual
from .shaders import Function, Varying
from ..gloo import VertexBuffer, IndexBuffer
from ..geometry import MeshData
from ..color import Color


# Shaders for lit rendering (using phong shading)
shading_vertex_template = """
varying vec3 v_normal_vec;
varying vec3 v_light_vec;
varying vec3 v_eye_vec;

varying vec4 v_ambientk;
varying vec4 v_light_color;
varying vec4 v_base_color;


void main() {

    v_ambientk = $ambientk;
    v_light_color = $light_color;
    v_base_color = $base_color;


    vec4 pos_scene = $visual2scene($to_vec4($position));
    vec4 normal_scene = $visual2scene(vec4($normal, 1.0));
    vec4 origin_scene = $visual2scene(vec4(0.0, 0.0, 0.0, 1.0));

    normal_scene /= normal_scene.w;
    origin_scene /= origin_scene.w;

    vec3 normal = normalize(normal_scene.xyz - origin_scene.xyz);
    v_normal_vec = normal; //VARYING COPY

    vec4 pos_front = $scene2doc(pos_scene);
    pos_front.z += 0.01;
    pos_front = $doc2scene(pos_front);
    pos_front /= pos_front.w;

    vec4 pos_back = $scene2doc(pos_scene);
    pos_back.z -= 0.01;
    pos_back = $doc2scene(pos_back);
    pos_back /= pos_back.w;

    vec3 eye = normalize(pos_front.xyz - pos_back.xyz);
    v_eye_vec = eye; //VARYING COPY

    vec3 light = normalize($light_dir.xyz);
    v_light_vec = light; //VARYING COPY

    gl_Position = $transform($to_vec4($position));
}
"""

shading_fragment_template = """
varying vec3 v_normal_vec;
varying vec3 v_light_vec;
varying vec3 v_eye_vec;

varying vec4 v_ambientk;
varying vec4 v_light_color;
varying vec4 v_base_color;

void main() {


    //DIFFUSE
    float diffusek = dot(v_light_vec, v_normal_vec);
    //clamp, because 0 < theta < pi/2
    diffusek  = clamp(diffusek, 0.0, 1.0);
    vec4 diffuse_color = v_light_color * diffusek;
    //diffuse_color.a = 1.0;

    //SPECULAR
    //reflect light wrt normal for the reflected ray, then
    //find the angle made with the eye
    float speculark = dot(reflect(v_light_vec, v_normal_vec), v_eye_vec);
    speculark = clamp(speculark, 0.0, 1.0);
    //raise to the material's shininess, multiply with a
    //small factor for spread
    speculark = 20.0 * pow(speculark, 200.0);

    vec4 specular_color = v_light_color * speculark;


    gl_FragColor =
       v_base_color * (v_ambientk + diffuse_color) + specular_color;

    //gl_FragColor = vec4(speculark, 0, 1, 1.0);


}
"""

# Shader code for non lighted rendering
vertex_template = """
void main() {
    gl_Position = $transform($to_vec4($position));
}
"""

fragment_template = """
void main() {
    gl_FragColor = $color;
}
"""


# Functions that can be used as is (don't have template variables)
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


class MeshVisual(Visual):
    """Mesh visual

    Parameters
    ----------
    vertices : array-like | None
        The vertices.
    faces : array-like | None
        The faces.
    vertex_colors : array-like | None
        Colors to use for each vertex.
    face_colors : array-like | None
        Colors to use for each face.
    color : instance of Color
        The color to use.
    meshdata : instance of MeshData | None
        The meshdata.
    shading : str | None
        Shading to use.
    mode : str
        The drawing mode.
    **kwargs : dict
        Keyword arguments to pass to `Visual`.
    """
    def __init__(self, vertices=None, faces=None, vertex_colors=None,
                 face_colors=None, color=(0.5, 0.5, 1, 1), meshdata=None,
                 shading=None, mode='triangles', **kwargs):

        # Function for computing phong shading
        # self._phong = Function(phong_template)

        # Visual.__init__ -> prepare_transforms() -> uses shading
        self.shading = shading

        if shading is not None:
            Visual.__init__(self, vcode=shading_vertex_template,
                            fcode=shading_fragment_template,
                            **kwargs)

        else:
            Visual.__init__(self, vcode=vertex_template,
                            fcode=fragment_template,
                            **kwargs)

        self.set_gl_state('translucent', depth_test=True,
                          cull_face=False)

        # Define buffers
        self._vertices = VertexBuffer(np.zeros((0, 3), dtype=np.float32))
        self._normals = None
        self._faces = IndexBuffer()
        self._colors = VertexBuffer(np.zeros((0, 4), dtype=np.float32))
        self._normals = VertexBuffer(np.zeros((0, 3), dtype=np.float32))

        # Uniform color
        self._color = Color(color)

        # varyings
        self._color_var = Varying('v_color', dtype='vec4')

        # Init
        self._bounds = None
        # Note we do not call subclass set_data -- often the signatures
        # do no match.
        MeshVisual.set_data(self, vertices=vertices, faces=faces,
                            vertex_colors=vertex_colors,
                            face_colors=face_colors, meshdata=meshdata,
                            color=color)

        # primitive mode
        self._draw_mode = mode
        self.freeze()

    def set_data(self, vertices=None, faces=None, vertex_colors=None,
                 face_colors=None, color=None, meshdata=None):
        """Set the mesh data

        Parameters
        ----------
        vertices : array-like | None
            The vertices.
        faces : array-like | None
            The faces.
        vertex_colors : array-like | None
            Colors to use for each vertex.
        face_colors : array-like | None
            Colors to use for each face.
        color : instance of Color
            The color to use.
        meshdata : instance of MeshData | None
            The meshdata.
        """
        if meshdata is not None:
            self._meshdata = meshdata
        else:
            self._meshdata = MeshData(vertices=vertices, faces=faces,
                                      vertex_colors=vertex_colors,
                                      face_colors=face_colors)
        self._bounds = self._meshdata.get_bounds()
        if color is not None:
            self._color = Color(color)
        self.mesh_data_changed()

    @property
    def mode(self):
        """The triangle mode used to draw this mesh.

        Options are:

            * 'triangles': Draw one triangle for every three vertices
              (eg, [1,2,3], [4,5,6], [7,8,9)
            * 'triangle_strip': Draw one strip for every vertex excluding the
              first two (eg, [1,2,3], [2,3,4], [3,4,5])
            * 'triangle_fan': Draw each triangle from the first vertex and the
              last two vertices (eg, [1,2,3], [1,3,4], [1,4,5])
        """
        return self._draw_mode

    @mode.setter
    def mode(self, m):
        modes = ['triangles', 'triangle_strip', 'triangle_fan']
        if m not in modes:
            raise ValueError("Mesh mode must be one of %s" % ', '.join(modes))
        self._draw_mode = m

    @property
    def mesh_data(self):
        """The mesh data"""
        return self._meshdata

    @property
    def color(self):
        """The uniform color for this mesh.

        This value is only used if per-vertex or per-face colors are not
        specified.
        """
        return self._color

    @color.setter
    def color(self, c):
        if c is not None:
            self._color = Color(c)
        self.mesh_data_changed()

    def mesh_data_changed(self):
        self._data_changed = True
        self.update()

    def _update_data(self):
        md = self.mesh_data
        # Update vertex/index buffers
        if self.shading == 'smooth' and not md.has_face_indexed_data():
            v = md.get_vertices()
            if v is None:
                return False
            if v.shape[-1] == 2:
                v = np.concatenate((v, np.zeros((v.shape[:-1] + (1,)))), -1)
            self._vertices.set_data(v, convert=True)
            self._normals.set_data(md.get_vertex_normals(), convert=True)
            self._faces.set_data(md.get_faces(), convert=True)
            self._index_buffer = self._faces
            if md.has_vertex_color():
                self._colors.set_data(md.get_vertex_colors(), convert=True)
            elif md.has_face_color():
                self._colors.set_data(md.get_face_colors(), convert=True)
            else:
                self._colors.set_data(np.zeros((0, 4), dtype=np.float32))
        else:
            v = md.get_vertices(indexed='faces')
            if v is None:
                return False
            if v.shape[-1] == 2:
                v = np.concatenate((v, np.zeros((v.shape[:-1] + (1,)))), -1)
            self._vertices.set_data(v, convert=True)
            if self.shading == 'smooth':
                normals = md.get_vertex_normals(indexed='faces')
                self._normals.set_data(normals, convert=True)
            elif self.shading == 'flat':
                normals = md.get_face_normals(indexed='faces')
                self._normals.set_data(normals, convert=True)
            else:
                self._normals.set_data(np.zeros((0, 3), dtype=np.float32))
            self._index_buffer = None
            if md.has_vertex_color():
                self._colors.set_data(md.get_vertex_colors(indexed='faces'),
                                      convert=True)
            elif md.has_face_color():
                self._colors.set_data(md.get_face_colors(indexed='faces'),
                                      convert=True)
            else:
                self._colors.set_data(np.zeros((0, 4), dtype=np.float32))
        self.shared_program.vert['position'] = self._vertices

        # Position input handling
        if v.shape[-1] == 2:
            self.shared_program.vert['to_vec4'] = vec2to4
        elif v.shape[-1] == 3:
            self.shared_program.vert['to_vec4'] = vec3to4
        else:
            raise TypeError("Vertex data must have shape (...,2) or (...,3).")

        # Color input handling
        # If non-lit shading is used, then just pass the colors
        # Otherwise, the shader uses a base_color to represent the underlying
        # color, which is then lit with the lighting model
        colors = self._colors if self._colors.size > 0 else self._color.rgba
        if self.shading is None:
            self.shared_program.vert[self._color_var] = colors

        # Shading
        if self.shading is None:
            self.shared_program.frag['color'] = self._color_var
        else:
            # Normal data comes via vertex shader
            if self._normals.size > 0:
                normals = self._normals
            else:
                normals = (1., 0., 0.)

            self.shared_program.vert['normal'] = normals
            self.shared_program.vert['base_color'] = colors

            # Additional phong properties
            self.shared_program.vert['light_dir'] = (10, 5, -5)
            self.shared_program.vert['light_color'] = (1.0, 1.0, 1.0, 1.0)
            self.shared_program.vert['ambientk'] = (0.3, 0.3, 0.3, 1.0)

        self._data_changed = False

    @property
    def shading(self):
        """ The shading method used.
        """
        return self._shading

    @shading.setter
    def shading(self, value):
        assert value in (None, 'flat', 'smooth')
        self._shading = value

    def _prepare_draw(self, view):
        if self._data_changed:
            if self._update_data() is False:
                return False
            self._data_changed = False

    def draw(self, *args, **kwds):
        Visual.draw(self, *args, **kwds)

    @staticmethod
    def _prepare_transforms(view):
        tr = view.transforms.get_transform()
        view.view_program.vert['transform'] = tr  # .simplified

        if view.shading is not None:
            visual2scene = view.transforms.get_transform('visual', 'scene')
            scene2doc = view.transforms.get_transform('scene', 'document')
            doc2scene = view.transforms.get_transform('document', 'scene')
            view.shared_program.vert['visual2scene'] = visual2scene
            view.shared_program.vert['scene2doc'] = scene2doc
            view.shared_program.vert['doc2scene'] = doc2scene

    def _compute_bounds(self, axis, view):
        if self._bounds is None:
            return None
        return self._bounds[axis]
