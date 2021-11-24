# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import numbers

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
    See
    `examples/basics/scene/mesh_texture.py
    <https://github.com/vispy/vispy/blob/main/examples/basics/scene/mesh_texture.py>`_
    example script.

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
    vec4 pos_scene = $render2scene(gl_Position);
    v_pos_scene = pos_scene;

    // Calculate normal
    vec4 normal_scene = $visual2scene(vec4($normal, 1.0));
    vec4 origin_scene = $visual2scene(vec4(0.0, 0.0, 0.0, 1.0));
    normal_scene /= normal_scene.w;
    origin_scene /= origin_scene.w;
    v_normal_vec = normalize(normal_scene.xyz - origin_scene.xyz);

    // Calculate eye vector per-vertex (to account for perspective)
    vec4 pos_doc = $scene2doc(pos_scene);
    pos_doc /= pos_doc.w;
    vec4 pos_front = pos_doc;
    vec4 pos_back = pos_doc;
    pos_front.z -= 1e-5;
    pos_back.z += 1e-5;
    pos_front = $doc2scene(pos_front);
    pos_back = $doc2scene(pos_back);
    // The eye vec eminates from the eye, pointing towards what is being viewed
    v_eye_vec = normalize(pos_back.xyz / pos_back.w - pos_front.xyz / pos_front.w);

    // Pass on light direction (the direction that the "photons" travel)
    v_light_vec = normalize($light_dir.xyz);
}
"""


shading_fragment_template = """
varying vec3 v_normal_vec;
varying vec3 v_light_vec;
varying vec3 v_eye_vec;
varying vec4 v_pos_scene;

void shade() {
    if ($shading_enabled != 1) {
        return;
    }

    vec3 base_color = gl_FragColor.rgb;
    vec4 ambient_coeff = $ambient_coefficient;
    vec4 diffuse_coeff = $diffuse_coefficient;
    vec4 specular_coeff = $specular_coefficient;
    vec4 ambient_light = $ambient_light;
    vec4 diffuse_light = $diffuse_light;
    vec4 specular_light = $specular_light;
    float shininess = $shininess;

    vec3 normal = v_normal_vec;
    if ($flat_shading == 1) {
        vec3 u = dFdx(v_pos_scene.xyz);
        vec3 v = dFdy(v_pos_scene.xyz);
        normal = cross(u, v);
        // Note(asnt): The normal calculated above always points in the
        // direction of the camera. Reintroduce the original orientation of the
        // face.
        normal = gl_FrontFacing ? normal : -normal;
    }
    normal = normalize(normal);

    vec3 light_vec = normalize(v_light_vec);
    vec3 eye_vec = normalize(v_eye_vec);

    // Ambient illumination.
    vec3 ambient = ambient_coeff.rgb * ambient_coeff.a
                   * ambient_light.rgb * ambient_light.a;

    // Diffuse illumination (light vec points towards the surface)
    float diffuse_factor = dot(-light_vec, normal);
    diffuse_factor = max(diffuse_factor, 0.0);
    vec3 diffuse = diffuse_factor
                   * diffuse_coeff.rgb * diffuse_coeff.a
                   * diffuse_light.rgb * diffuse_light.a;

    // Specular illumination. Both light_vec and eye_vec point towards the surface.
    float specular_factor = 0.0;
    bool is_illuminated = diffuse_factor > 0.0;
    if (is_illuminated && shininess > 0.0) {
        // Phong reflection
        //vec3 reflection = reflect(-light_vec, normal);
        //float reflection_factor = max(dot(reflection, eye_vec), 0.0);
        // Blinn-Phong reflection
        vec3 halfway = -normalize(light_vec + eye_vec);
        float reflection_factor = clamp(dot(halfway, normal), 0.0, 1.0);
        specular_factor = pow(reflection_factor, shininess);
    }
    vec3 specular = specular_factor
                    * specular_coeff.rgb * specular_coeff.a
                    * specular_light.rgb * specular_light.a;

    // Blend the base color and combine the illuminations.
    vec3 color = base_color * (ambient + diffuse) + specular;
    gl_FragColor.rgb = color;
}
"""  # noqa


def _as_rgba(intensity_or_color, default_rgb=(1.0, 1.0, 1.0)):
    """Create an RGBA color from a color or a scalar intensity.

    Examples
    --------
    >>> # Specify the full RGBA color.
    >>> _as_rgba((0.2, 0.3, 0.4, 0.25))
    ... <Color: (0.2, 0.3, 0.4, 0.25)>
    >>> # Specify an RGB color. (Default intensity `1.0` is used.)
    >>> _as_rgba((0.2, 0.3, 0.4))
    ... <Color: (0.2, 0.3, 0.4, 1.0)>
    >>> # Specify an intensity only. (Default color `(1.0, 1.0, 1.0)` is used.)
    >>> _as_rgba(0.25)
    ... <Color: (1.0, 1.0, 1.0, 0.25)>
    """
    if isinstance(intensity_or_color, numbers.Number):
        intensity = intensity_or_color
        return Color(default_rgb, alpha=intensity)
    color = intensity_or_color
    return Color(color)


class ShadingFilter(Filter):
    """Apply shading to a :class:`~vispy.visuals.mesh.MeshVisual` using the Phong reflection model.

    For convenience, a :class:`~vispy.visuals.mesh.MeshVisual` creates and
    embeds a shading filter when constructed with an explicit `shading`
    parameter, e.g. `mesh = MeshVisual(..., shading='smooth')`. The filter is
    then accessible as `mesh.shading_filter`.

    When attached manually to a :class:`~vispy.visuals.mesh.MeshVisual`, the
    shading filter should come after any other filter that modifies the base
    color to be shaded. See the examples below.

    Parameters
    ----------
    shading : str
        Shading mode: None, 'flat' or 'smooth'. If None, the shading is
        disabled.
    ambient_coefficient : str or tuple or Color
        Color and intensity of the ambient reflection coefficient (Ka).
    diffuse_coefficient : str or tuple or Color
        Color and intensity of the diffuse reflection coefficient (Kd).
    specular_coefficient : str or tuple or Color
        Color and intensity of the specular reflection coefficient (Ks).
    shininess : float
        The shininess controls the size of specular highlight. The higher, the
        more localized.  Must be greater than or equal to zero.
    light_dir : array_like
        Direction of the light. Assuming a directional light.
    ambient_light : str or tuple or Color
        Color and intensity of the ambient light.
    diffuse_light : str or tuple or Color
        Color and intensity of the diffuse light.
    specular_light : str or tuple or Color
        Color and intensity of the specular light.
    enabled : bool, default=True
        Whether the filter is enabled at creation time. This can be changed at
        run time with :obj:`~enabled`.

    Notes
    -----
    Under the Phong reflection model, the illumination `I` is computed as::

        I = I_ambient + mesh_color * I_diffuse + I_specular

    for each color channel independently.
    `mesh_color` is the color of the :class:`~vispy.visuals.mesh.MeshVisual`,
    possibly modified by the filters applied before this one.
    The ambient, diffuse and specular terms are defined as::

        I_ambient = Ka * Ia
        I_diffuse = Kd * Id * dot(L, N)
        I_specular = Ks * Is * dot(R, V) ** s

    with

    `L`
        the light direction, assuming a directional light,
    `N`
        the normal to the surface at the reflection point,
    `R`
        the direction of the reflection,
    `V`
        the direction to the viewer,
    `s`
        the shininess factor.

    The `Ka`, `Kd` and `Ks` coefficients are defined as an RGBA color. The RGB
    components define the color that the surface reflects, and the alpha
    component (A) defines the intensity/attenuation of the reflection. When
    applied in the per-channel illumation formulas above, the color component
    is multiplied by the intensity to obtain the final coefficient, e.g.
    `Kd = R * A` for the red channel.

    Similarly, the light intensities, `Ia`, `Id` and `Is`, are defined by RGBA
    colors, corresponding to the color of the light and its intensity.

    Examples
    --------
    Define the mesh data for a :class:`vispy.visuals.mesh.MeshVisual`:

    >>> # A triangle.
    >>> vertices = np.array([(0, 0, 0), (1, 1, 1), (0, 1, 0)], dtype=float)
    >>> faces = np.array([(0, 1, 2)], dtype=int)

    Let the :class:`vispy.visuals.mesh.MeshVisual` create and embed a shading
    filter:

    >>> mesh = MeshVisual(vertices, faces, shading='smooth')
    >>> # Configure the filter afterwards.
    >>> mesh.shading_filter.shininess = 64
    >>> mesh.shading_filter.specular_coefficient = 0.3

    Create the shading filter manually and attach it to a
    :class:`vispy.visuals.mesh.MeshVisual`:

    >>> # With the default shading parameters.
    >>> shading_filter = ShadingFilter()
    >>> mesh = MeshVisual(vertices, faces)
    >>> mesh.attach(shading_filter)

    The filter can be configured at creation time and at run time:

    >>> # Configure at creation time.
    >>> shading_filter = ShadingFilter(
    ...     # A shiny surface (small specular highlight).
    ...     shininess=250,
    ...     # A blue higlight, at half intensity.
    ...     specular_coefficient=(0, 0, 1, 0.5),
    ...     # Equivalent to `(0.7, 0.7, 0.7, 1.0)`.
    ...     diffuse_coefficient=0.7,
    ...     # Same as `(0.2, 0.3, 0.3, 1.0)`.
    ...     ambient_coefficient=(0.2, 0.3, 0.3),
    ... )
    >>> # Change the configuration at run time.
    >>> shading_filter.shininess = 64
    >>> shading_filter.specular_coefficient = 0.3

    Disable the filter temporarily:

    >>> # Turn off the shading.
    >>> shading_filter.enabled = False
    ... # Some time passes...
    >>> # Turn on the shading again.
    >>> shading_filter.enabled = True

    When using the :class:`WireframeFilter`, the wireframe is shaded only if
    the wireframe filter is attached before the shading filter:

    >>> shading_filter = ShadingFilter()
    >>> wireframe_filter = WireframeFilter()
    >>> # Option 1: Shade the wireframe.
    >>> mesh1 = MeshVisual(vertices, faces)
    >>> mesh1.attached(wireframe_filter)
    >>> mesh1.attached(shading_filter)
    >>> # Option 2: Do not shade the wireframe.
    >>> mesh2 = MeshVisual(vertices, faces)
    >>> mesh2.attached(shading_filter)
    >>> mesh2.attached(wireframe_filter)

    See also
    `examples/basics/scene/mesh_shading.py
    <https://github.com/vispy/vispy/blob/main/examples/basics/scene/mesh_shading.py>`_
    example script.
    """

    def __init__(self, shading='flat',
                 ambient_coefficient=(1, 1, 1, 1),
                 diffuse_coefficient=(1, 1, 1, 1),
                 specular_coefficient=(1, 1, 1, 1),
                 shininess=100,
                 light_dir=(10, 5, -5),
                 ambient_light=(1, 1, 1, .25),
                 diffuse_light=(1, 1, 1, 0.7),
                 specular_light=(1, 1, 1, .25),
                 enabled=True):
        self._shading = shading

        self._ambient_coefficient = _as_rgba(ambient_coefficient)
        self._diffuse_coefficient = _as_rgba(diffuse_coefficient)
        self._specular_coefficient = _as_rgba(specular_coefficient)
        self._shininess = shininess

        self._light_dir = light_dir
        self._ambient_light = _as_rgba(ambient_light)
        self._diffuse_light = _as_rgba(diffuse_light)
        self._specular_light = _as_rgba(specular_light)

        self._enabled = enabled

        vfunc = Function(shading_vertex_template)
        ffunc = Function(shading_fragment_template)

        self._normals = VertexBuffer(np.zeros((0, 3), dtype=np.float32))
        vfunc['normal'] = self._normals

        super().__init__(vcode=vfunc, fcode=ffunc)

    @property
    def enabled(self):
        """True to enable the filter, False to disable."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled
        self._update_data()

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
    def ambient_light(self):
        """The color and intensity of the ambient light."""
        return self._ambient_light

    @ambient_light.setter
    def ambient_light(self, light_color):
        self._ambient_light = _as_rgba(light_color)
        self._update_data()

    @property
    def diffuse_light(self):
        """The color and intensity of the diffuse light."""
        return self._diffuse_light

    @diffuse_light.setter
    def diffuse_light(self, light_color):
        self._diffuse_light = _as_rgba(light_color)
        self._update_data()

    @property
    def specular_light(self):
        """The color and intensity of the specular light."""
        return self._specular_light

    @specular_light.setter
    def specular_light(self, light_color):
        self._specular_light = _as_rgba(light_color)
        self._update_data()

    @property
    def ambient_coefficient(self):
        """The ambient reflection coefficient."""
        return self._ambient_coefficient

    @ambient_coefficient.setter
    def ambient_coefficient(self, color):
        self._ambient_coefficient = _as_rgba(color)
        self._update_data()

    @property
    def diffuse_coefficient(self):
        """The diffuse reflection coefficient."""
        return self._diffuse_coefficient

    @diffuse_coefficient.setter
    def diffuse_coefficient(self, diffuse_coefficient):
        self._diffuse_coefficient = _as_rgba(diffuse_coefficient)
        self._update_data()

    @property
    def specular_coefficient(self):
        """The specular reflection coefficient."""
        return self._specular_coefficient

    @specular_coefficient.setter
    def specular_coefficient(self, specular_coefficient):
        self._specular_coefficient = _as_rgba(specular_coefficient)
        self._update_data()

    @property
    def shininess(self):
        """The shininess controlling the spread of the specular highlight."""
        return self._shininess

    @shininess.setter
    def shininess(self, shininess):
        self._shininess = float(shininess)
        self._update_data()

    def _update_data(self):
        if not self._attached:
            return

        self.vshader['light_dir'] = self._light_dir

        self.fshader['ambient_light'] = self._ambient_light.rgba
        self.fshader['diffuse_light'] = self._diffuse_light.rgba
        self.fshader['specular_light'] = self._specular_light.rgba

        self.fshader['ambient_coefficient'] = self._ambient_coefficient.rgba
        self.fshader['diffuse_coefficient'] = self._diffuse_coefficient.rgba
        self.fshader['specular_coefficient'] = self._specular_coefficient.rgba
        self.fshader['shininess'] = self._shininess

        self.fshader['flat_shading'] = 1 if self._shading == 'flat' else 0
        self.fshader['shading_enabled'] = (
            1 if self._enabled and self._shading is not None else 0
        )

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

        if self._visual.mesh_data is not None:
            self._update_data()

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
    if ($enabled != 1) {
        return;
    }

    vec3 d = fwidth(v_bc);  // relative distance to edge
    vec3 fading3 = smoothstep(vec3(0.0), $width * d, v_bc);
    float opacity = 1.0 - min(min(fading3.x, fading3.y), fading3.z);

    if ($wireframe_only == 1) {
        if (opacity == 0.0) {
            // Inside a triangle.
            discard;
        }
        // On the edge.
        gl_FragColor = $color;
        gl_FragColor.a = opacity;
    } else if ($faces_only == 1) {
        if (opacity == 1.0) {
            // Inside an edge.
            discard;
        }
        // Inside a triangle.
        gl_FragColor.a = 1.0 - opacity;
    } else {
        gl_FragColor = mix(gl_FragColor, $color, opacity);
    }

}
"""  # noqa


class WireframeFilter(Filter):
    """Add wireframe to a mesh.

    The wireframe filter should be attached before the shading filter for the
    wireframe to be shaded.

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
    See
    `examples/basics/scene/mesh_shading.py
    <https://github.com/vispy/vispy/blob/main/examples/basics/scene/mesh_shading.py>`_
    example script.

    """

    def __init__(self, enabled=True, color='black', width=1.0,
                 wireframe_only=False, faces_only=False):
        self._attached = False
        self._color = Color(color)
        self._width = width
        self._enabled = enabled
        self._wireframe_only = wireframe_only
        self._faces_only = faces_only

        vfunc = Function(wireframe_vertex_template)
        ffunc = Function(wireframe_fragment_template)

        self._bc = VertexBuffer(np.zeros((0, 3), dtype=np.float32))
        vfunc['bc'] = self._bc

        super().__init__(vcode=vfunc, fcode=ffunc)
        self.enabled = enabled

    @property
    def enabled(self):
        """True to enable the display of the wireframe, False to disable."""
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

    @property
    def wireframe_only(self):
        """Draw only the wireframe and discard the interior of the faces."""
        return self._wireframe_only

    @wireframe_only.setter
    def wireframe_only(self, wireframe_only):
        self._wireframe_only = wireframe_only
        self._update_data()

    @property
    def faces_only(self):
        """Make the wireframe transparent.

        Draw only the interior of the faces.
        """
        return self._faces_only

    @faces_only.setter
    def faces_only(self, faces_only):
        self._faces_only = faces_only
        self._update_data()

    def _update_data(self):
        if not self.attached:
            return
        self.fshader['color'] = self._color.rgba
        self.fshader['width'] = self._width
        self.fshader['wireframe_only'] = 1 if self._wireframe_only else 0
        self.fshader['faces_only'] = 1 if self._faces_only else 0
        if self._visual.mesh_data.is_empty():
            n_faces = 0
        else:
            n_faces = len(self._visual.mesh_data.get_faces())
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
