# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import numpy as np
from vispy.gloo import Texture2D, VertexBuffer
from vispy.visuals.shaders import Function, Varying
from vispy.visuals.filters import Filter
from ...color import Color


class TextureFilter(Filter):
    """Filter to apply a texture to a mesh.

    Note the texture is applied by multiplying the texture color by the
    Visual's produced color. By specifying `color="white"` when creating
    a `MeshVisual` the result will be the unaltered texture value. Any
    other color, including the default, will result in a blending of that
    color and the color of the texture.

    Parameters
    ----------
    texture : (M, N) or (M, N, C) array
        The 2D texture image.
    texcoords : (N, 2) array
        The texture coordinates.
    enabled : bool
        Whether the display of the texture is enabled.

    Examples
    --------
    See ``examples/basics/scene/mesh_texture.py`` example script.

    """

    def __init__(self, texture, texcoords, enabled=True):
        """Apply a texture on a mesh."""
        vfunc = Function("""
            void pass_coords() {
                $v_texcoords = $texcoords;
            }
        """)
        ffunc = Function("""
            void apply_texture() {
                if ($enabled == 1) {
                    gl_FragColor *= texture2D($u_texture, $texcoords);
                }
            }
        """)
        self._texcoord_varying = Varying('v_texcoord', 'vec2')
        vfunc['v_texcoords'] = self._texcoord_varying
        ffunc['texcoords'] = self._texcoord_varying
        self._texcoords_buffer = VertexBuffer(
            np.zeros((0, 2), dtype=np.float32)
        )
        vfunc['texcoords'] = self._texcoords_buffer
        super().__init__(vcode=vfunc, vhook='pre', fcode=ffunc)

        self.enabled = enabled
        self.texture = texture
        self.texcoords = texcoords

    @property
    def enabled(self):
        """True to display the texture, False to disable."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled
        self.fshader['enabled'] = 1 if enabled else 0

    @property
    def texture(self):
        """The texture image."""
        return self._texture

    @texture.setter
    def texture(self, texture):
        self._texture = texture
        self.fshader['u_texture'] = Texture2D(texture)

    @property
    def texcoords(self):
        """The texture coordinates as an (N, 2) array of floats."""
        return self._texcoords

    @texcoords.setter
    def texcoords(self, texcoords):
        self._texcoords = texcoords
        self._update_texcoords_buffer(texcoords)

    def _update_texcoords_buffer(self, texcoords):
        if not self._attached or self._visual is None:
            return

        # FIXME: Indices for texture coordinates might be different than face
        # indices, although in some cases they are the same. Currently,
        # vispy.io.read_mesh assumes face indices and texture coordinates are
        # the same.
        # TODO:
        # 1. Add reading and returning of texture coordinate indices in
        #    read_mesh.
        # 2. Add texture coordinate indices in MeshData from
        #    vispy.geometry.meshdata
        # 3. Use mesh_data.get_texcoords_indices() here below.
        tc = texcoords[self._visual.mesh_data.get_faces()]
        self._texcoords_buffer.set_data(tc, convert=True)

    def _attach(self, visual):
        super()._attach(visual)
        self._update_texcoords_buffer(self._texcoords)


shading_vertex_template = """
varying vec3 v_normal_vec;
varying vec3 v_light_vec;
varying vec3 v_eye_vec;
varying vec4 v_pos_scene;

void prepare_shading() {
    // TODO: Find a way to get the original position from the main vertex
    //       shader instead of inversing the transformation.
    vec4 pos_scene = $render2scene(gl_Position);
    v_pos_scene = pos_scene; // Used in the fragment for flat shading.

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
}
"""

shading_fragment_template = """
varying vec3 v_normal_vec;
varying vec3 v_light_vec;
varying vec3 v_eye_vec;
varying vec4 v_pos_scene;

void shade() {
    vec3 normal;
    if ($flat_shading == 1) {
        vec3 u = dFdx(v_pos_scene.xyz);
        vec3 v = dFdy(v_pos_scene.xyz);
        normal = normalize(cross(u, v));
    } else {
        normal = v_normal_vec;
    }

    vec3 light_vec = v_light_vec;

    // Diffuse light component.
    float diffusek = dot(light_vec, normal);
    diffusek  = max(diffusek, 0.0);
    vec3 diffuse_color = $light_color * $diffuse_color * diffusek;

    // Specular light component.
    float speculark = 0.0;
    if ($shininess > 0) {
        vec3 reflexion = reflect(light_vec, normal);
        speculark = dot(reflexion, v_eye_vec);
        speculark = max(speculark, 0.0);
        speculark = pow(speculark, $shininess);
    }
    vec3 specular_color = $light_color * $specular_color * speculark;

    if ($shading_enabled == 1) {
        vec3 color = $ambient_color + diffuse_color + specular_color;
        gl_FragColor *= vec4(color, 1.0);
    }
}
"""  # noqa


class ShadingFilter(Filter):
    """Filter to apply shading to a mesh.

    To disable shading, either detach (ex. ``mesh.detach(filter_obj)``) or
    set the shading type to ``None`` (ex. ``filter_obj.shading = None``).

    Examples
    --------
    See ``examples/basics/scene/mesh_shading.py`` example script.

    """

    def __init__(self, shading='flat', light_dir=(10, 5, -5),
                 light_color=(1, 1, 1, 1),
                 ambient_color=(.3, .3, .3, 1),
                 diffuse_color=(1, 1, 1, 1),
                 specular_color=(1, 1, 1, 1),
                 shininess=100):
        self._shading = shading
        self._light_dir = light_dir
        self._light_color = Color(light_color)
        self._ambient_color = Color(ambient_color)
        self._diffuse_color = Color(diffuse_color)
        self._specular_color = Color(specular_color)
        self._shininess = shininess

        vfunc = Function(shading_vertex_template)
        ffunc = Function(shading_fragment_template)

        self._normals = VertexBuffer(np.zeros((0, 3), dtype=np.float32))
        vfunc['normal'] = self._normals

        super().__init__(vcode=vfunc, fcode=ffunc)

    @property
    def shading(self):
        """The shading method."""
        return self._shading

    @shading.setter
    def shading(self, shading):
        assert shading in (None, 'flat', 'smooth')
        self._shading = shading
        self._update_data()

    @property
    def light_dir(self):
        """The light direction."""
        return self._light_dir

    @light_dir.setter
    def light_dir(self, direction):
        direction = np.array(direction, float).ravel()
        if direction.size != 3 or not np.isfinite(direction).all():
            raise ValueError('Invalid direction %s' % direction)
        self._light_dir = tuple(direction)
        self._update_data()

    @property
    def light_color(self):
        """The light color."""
        return self._light_color

    @light_color.setter
    def light_color(self, light_color):
        self._light_color = Color(light_color)
        self._update_data()

    @property
    def diffuse_color(self):
        """The diffuse light color."""
        return self._diffuse_color

    @diffuse_color.setter
    def diffuse_color(self, diffuse_color):
        self._diffuse_color = Color(diffuse_color)
        self._update_data()

    @property
    def specular_color(self):
        """The specular light color."""
        return self._specular_color

    @specular_color.setter
    def specular_color(self, specular_color):
        self._specular_color = Color(specular_color)
        self._update_data()

    @property
    def ambient_color(self):
        """The ambient color."""
        return self._ambient_color

    @ambient_color.setter
    def ambient_color(self, color):
        self._ambient_color = Color(color)
        self._update_data()

    @property
    def shininess(self):
        """The shininess."""
        return self._shininess

    @shininess.setter
    def shininess(self, shininess):
        self._shininess = float(shininess)
        self._update_data()

    def _update_data(self):
        if not self._attached:
            return
        self.vshader['light_dir'] = self._light_dir
        self.fshader['shininess'] = self._shininess
        self.fshader['light_color'] = self._light_color.rgb
        self.fshader['ambient_color'] = self._ambient_color.rgb
        self.fshader['diffuse_color'] = self._diffuse_color.rgb
        self.fshader['specular_color'] = self._specular_color.rgb
        self.fshader['flat_shading'] = 1 if self._shading == 'flat' else 0
        self.fshader['shading_enabled'] = 1 if self._shading is not None else 0
        normals = self._visual.mesh_data.get_vertex_normals(indexed='faces')
        self._normals.set_data(normals, convert=True)

    def on_mesh_data_updated(self, event):
        self._update_data()

    def _attach(self, visual):
        super()._attach(visual)

        render2scene = visual.transforms.get_transform('render', 'scene')
        visual2scene = visual.transforms.get_transform('visual', 'scene')
        scene2doc = visual.transforms.get_transform('scene', 'document')
        doc2scene = visual.transforms.get_transform('document', 'scene')
        self.vshader['render2scene'] = render2scene
        self.vshader['visual2scene'] = visual2scene
        self.vshader['scene2doc'] = scene2doc
        self.vshader['doc2scene'] = doc2scene

        visual.events.data_updated.connect(self.on_mesh_data_updated)

    def _detach(self, visual):
        visual.events.data_updated.disconnect(self.on_mesh_data_updated)
        super()._detach(visual)


wireframe_vertex_template = """
varying vec3 v_bc;

void prepare_wireframe() {
    v_bc = $bc;
}
"""  # noqa


wireframe_fragment_template = """
varying vec3 v_bc;

void draw_wireframe() {
    vec3 d = fwidth(v_bc);
    vec3 a3 = smoothstep(vec3(0.0), $width * d, v_bc);
    float factor = min(min(a3.x, a3.y), a3.z);
    if ($enabled == 1) {
        gl_FragColor = mix($color, gl_FragColor, factor);
    } else {
        gl_FragColor = gl_FragColor;
    }
}
"""  # noqa


class WireframeFilter(Filter):
    """Add wireframe to a mesh.

    Parameters
    ----------
    color : str or tuple or Color
        Line color of the wireframe
    width : float
        Line width of the wireframe
    enabled : bool
        Whether the wireframe is drawn or not

    Examples
    --------
    See ``examples/basics/scene/mesh_shading.py`` example script.

    """

    def __init__(self, enabled=True, color='black', width=1.0):
        self._attached = False
        self._color = Color(color)
        self._width = width
        self._enabled = False

        vfunc = Function(wireframe_vertex_template)
        ffunc = Function(wireframe_fragment_template)

        self._bc = VertexBuffer(np.zeros((0, 3), dtype=np.float32))
        vfunc['bc'] = self._bc

        super().__init__(vcode=vfunc, fcode=ffunc)
        self.enabled = enabled

    @property
    def enabled(self):
        """True to enable shading."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled
        self.fshader['enabled'] = 1 if enabled else 0
        self._update_data()

    @property
    def color(self):
        """The wireframe color."""
        return self._color

    @color.setter
    def color(self, color):
        self._color = Color(color)
        self._update_data()

    @property
    def width(self):
        """The wireframe width."""
        return self._width

    @width.setter
    def width(self, width):
        if width < 0:
            raise ValueError("width must be greater than zero")
        self._width = width
        self._update_data()

    def _update_data(self):
        if not self.attached:
            return
        self.fshader['color'] = self._color.rgba
        self.fshader['width'] = self._width
        faces = self._visual.mesh_data.get_faces()
        n_faces = len(faces)
        bc = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype='float')
        bc = np.tile(bc[None, ...], (n_faces, 1, 1))
        self._bc.set_data(bc, convert=True)

    def on_mesh_data_updated(self, event):
        self._update_data()

    def _attach(self, visual):
        super()._attach(visual)
        visual.events.data_updated.connect(self.on_mesh_data_updated)

    def _detach(self, visual):
        visual.events.data_updated.disconnect(self.on_mesh_data_updated)
        super()._detach(visual)
