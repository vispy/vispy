# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

""" A MeshVisual Visual that uses the new shader Function.
"""

from __future__ import division

import numpy as np

from .visual import Visual
from .shaders import Function, FunctionChain
from ..gloo import VertexBuffer, IndexBuffer
from ..geometry import MeshData
from ..color import Color, get_colormap
from ..ext.six import string_types

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
    v_base_color = $color_transform($base_color);


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
    // clamp, because 0 < theta < pi/2
    diffusek  = clamp(diffusek, 0.0, 1.0);
    vec4 diffuse_color = v_light_color * diffusek;

    //SPECULAR
    //reflect light wrt normal for the reflected ray, then
    //find the angle made with the eye
    float speculark = 0.0;
    if ($shininess > 0.) {
        speculark = dot(reflect(v_light_vec, v_normal_vec), v_eye_vec);
        speculark = clamp(speculark, 0.0, 1.0);
        //raise to the material's shininess, multiply with a
        //small factor for spread
        speculark = 20.0 * pow(speculark, 1.0 / $shininess);
    }
    vec4 specular_color = v_light_color * speculark;
    gl_FragColor = v_base_color * (v_ambientk + diffuse_color) + specular_color;
}
"""  # noqa

# Shader code for non lighted rendering
vertex_template = """
varying vec4 v_base_color;

void main() {
    v_base_color = $color_transform($base_color);
    gl_Position = $transform($to_vec4($position));
}
"""

fragment_template = """
varying vec4 v_base_color;
void main() {
    gl_FragColor = v_base_color;
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


_null_color_transform = 'vec4 pass(vec4 color) { return color; }'
_clim = 'float cmap(float val) { return (val - $cmin) / ($cmax - $cmin); }'


# Eventually this could be de-duplicated with visuals/image.py, which does
# something similar (but takes a ``color`` instead of ``float``)
def _build_color_transform(data, cmap, clim=(0., 1.)):
    if data.ndim == 2 and data.shape[1] == 1:
        fun = Function(_clim)
        fun['cmin'] = clim[0]
        fun['cmax'] = clim[1]
        fun = FunctionChain(None, [fun, Function(cmap.glsl_map)])
    else:
        fun = Function(_null_color_transform)
    return fun


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
    vertex_values : array-like | None
        The values to use for each vertex (for colormapping).
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
                 face_colors=None, color=(0.5, 0.5, 1, 1), vertex_values=None,
                 meshdata=None, shading=None, mode='triangles', **kwargs):

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
        self._normals = VertexBuffer(np.zeros((0, 3), dtype=np.float32))
        self._ambient_light_color = Color((0.3, 0.3, 0.3, 1.0))
        self._light_dir = (10, 5, -5)
        self._shininess = 1. / 200.
        self._cmap = get_colormap('cubehelix')
        self._clim = 'auto'

        # Uniform color
        self._color = Color(color)

        # Init
        self._bounds = None
        # Note we do not call subclass set_data -- often the signatures
        # do no match.
        MeshVisual.set_data(
            self, vertices=vertices, faces=faces, vertex_colors=vertex_colors,
            face_colors=face_colors, vertex_values=vertex_values,
            meshdata=meshdata, color=color)

        # primitive mode
        self._draw_mode = mode
        self.freeze()

    def set_data(self, vertices=None, faces=None, vertex_colors=None,
                 face_colors=None, color=None, vertex_values=None,
                 meshdata=None):
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
        vertex_values : array-like | None
            Values for each vertex.
        meshdata : instance of MeshData | None
            The meshdata.
        """
        if meshdata is not None:
            self._meshdata = meshdata
        else:
            self._meshdata = MeshData(vertices=vertices, faces=faces,
                                      vertex_colors=vertex_colors,
                                      face_colors=face_colors,
                                      vertex_values=vertex_values)
        self._bounds = self._meshdata.get_bounds()
        if color is not None:
            self._color = Color(color)
        self.mesh_data_changed()

    @property
    def clim(self):
        return (self._clim if isinstance(self._clim, string_types) else
                tuple(self._clim))

    @clim.setter
    def clim(self, clim):
        if isinstance(clim, string_types):
            if clim != 'auto':
                raise ValueError('clim must be "auto" if a string')
        else:
            clim = np.array(clim, float)
            if clim.shape != (2,):
                raise ValueError('clim must have two elements')
        self._clim = clim
        self.mesh_data_changed()

    @property
    def _clim_values(self):
        if isinstance(self._clim, string_types):  # == 'auto'
            if self._meshdata.has_vertex_value():
                clim = self._meshdata.get_vertex_values()
                clim = (np.min(clim), np.max(clim))
            else:
                clim = (0, 1)
        else:
            clim = self._clim
        return clim

    @property
    def cmap(self):
        return self._cmap

    @cmap.setter
    def cmap(self, cmap):
        self._cmap = get_colormap(cmap)
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
        """The uniform color for this mesh"""
        return self._color

    @color.setter
    def color(self, c):
        """Set the uniform color of the mesh

        This value is only used if per-vertex or per-face colors are not
        specified.

        Parameters
        ----------
        c : instance of Color
            The color to use.
        """
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
                colors = md.get_vertex_colors()
                colors = colors.astype(np.float32)
            elif md.has_face_color():
                colors = md.get_face_colors()
                colors = colors.astype(np.float32)
            elif md.has_vertex_value():
                colors = md.get_vertex_values()[:, np.newaxis]
                colors = colors.astype(np.float32)
            else:
                colors = self._color.rgba
        else:
            # It might actually be slower to prefer the indexed='faces' mode.
            # It certainly adds some complexity, and I'm not sure what the
            # benefits are, or if they justify this additional complexity.
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
                colors = md.get_vertex_colors(indexed='faces')
                colors = colors.astype(np.float32)
            elif md.has_face_color():
                colors = md.get_face_colors(indexed='faces')
                colors = colors.astype(np.float32)
            elif md.has_vertex_value():
                colors = md.get_vertex_values(indexed='faces')
                colors = colors.ravel()[:, np.newaxis]
                colors = colors.astype(np.float32)
            else:
                colors = self._color.rgba
        self.shared_program.vert['position'] = self._vertices

        self.shared_program['texture2D_LUT'] = self._cmap.texture_lut() \
            if (hasattr(self._cmap, 'texture_lut')) else None

        # Position input handling
        if v.shape[-1] == 2:
            self.shared_program.vert['to_vec4'] = vec2to4
        elif v.shape[-1] == 3:
            self.shared_program.vert['to_vec4'] = vec3to4
        else:
            raise TypeError("Vertex data must have shape (...,2) or (...,3).")

        # Shading and colors
        #
        # If non-lit shading is used, then just pass the colors
        # Otherwise, the shader uses a base_color to represent the underlying
        # color, which is then lit with the lighting model
        self.shared_program.vert['color_transform'] = \
            _build_color_transform(colors, self._cmap, self._clim_values)
        if colors.ndim == 1:
            self.shared_program.vert['base_color'] = colors
        else:
            self.shared_program.vert['base_color'] = VertexBuffer(colors)
        if self.shading is not None:
            # Normal data comes via vertex shader
            if self._normals.size > 0:
                normals = self._normals
            else:
                normals = (1., 0., 0.)

            self.shared_program.vert['normal'] = normals

            # Additional phong properties
            self.shared_program.vert['light_dir'] = self._light_dir
            self.shared_program.vert['light_color'] = (1.0, 1.0, 1.0, 1.0)
            self.shared_program.vert['ambientk'] = \
                self._ambient_light_color.rgba
            self.shared_program.frag['shininess'] = self._shininess

        self._data_changed = False

    @property
    def shininess(self):
        """The shininess"""
        return self._shininess

    @shininess.setter
    def shininess(self, shine):
        """Set the shininess

        Parameters
        ----------
        shine : float
            The shininess to use.
        """
        self._shininess = float(shine)
        self.mesh_data_changed()

    @property
    def ambient_light_color(self):
        """The ambient light color"""
        return self._ambient_light_color

    @ambient_light_color.setter
    def ambient_light_color(self, ambient):
        """Set the ambient light

        Parameters
        ----------
        color : instance of Color
            The color to use.
        """
        self._ambient_light_color = Color(ambient)
        self.mesh_data_changed()

    @property
    def light_dir(self):
        """The light direction"""
        return self._light_dir

    @light_dir.setter
    def light_dir(self, direction):
        """Set the light direction

        Parameters
        ----------
        direction : ndarray, shape (3,)
            The light direction.
        """
        direction = np.array(direction, float).ravel()
        if direction.size != 3 or not np.isfinite(direction).all():
            raise ValueError('Invalid direction %s' % direction)
        self._light_dir = tuple(direction)
        self.mesh_data_changed()

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
        if axis >= len(self._bounds):
            return (0, 0)
        else:
            return self._bounds[axis]
