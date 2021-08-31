# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""Pseudo spheres (shaded discs) visual"""

import numpy as np

from ..color import ColorArray
from ..gloo import VertexBuffer
from .visual import Visual


vert = """
uniform vec3 u_light_position;

attribute vec3 a_position;
attribute vec4 a_color;
attribute float a_radius;

varying vec4 v_color;
varying vec3 v_light_direction;
varying float v_depth_middle;

float big_float = 1e10; // prevents numerical imprecision

void main (void) {
    v_color = a_color;
    v_light_direction = normalize(u_light_position);

    vec4 pos = vec4(a_position, 1);
    vec4 fb_pos = $visual_to_framebuffer(pos);
    gl_Position = $framebuffer_to_render(fb_pos);

    // NOTE: gl_stuff uses framebuffer coords!

    // calculate point size from visual to framebuffer coords to determine radius
    vec4 x = $framebuffer_to_visual(fb_pos + vec4(big_float, 0, 0, 0));
    x = (x - pos);
    vec4 radius_vec = $visual_to_framebuffer(pos + normalize(x) * a_radius);
    float radius_px = radius_vec.x / radius_vec.w - fb_pos.x / fb_pos.w;

    // gl_PointSize is the diameter
    gl_PointSize = radius_px * 2;

    // Get the framebuffer z direction relative to this sphere in visual coords
    vec4 z = $framebuffer_to_visual(fb_pos + vec4(0, 0, big_float, 0));
    z = (z - pos);
    // Get the depth of the sphere in its middle point on the screen (+ radius)
    vec4 depth_z_vec = $visual_to_framebuffer(pos + normalize(z) * a_radius);
    v_depth_middle = depth_z_vec.z / depth_z_vec.w - fb_pos.z / fb_pos.w;
}
"""


frag = """
uniform vec3 u_light_color;
uniform float u_light_ambient;
uniform float u_alpha;

varying vec4 v_color;
varying vec3 v_light_direction;
varying float v_depth_middle;

void main()
{
    // discard fragments outside of disc
    vec2 texcoord = gl_PointCoord * 2 - 1;
    float x = texcoord.x;
    float y = texcoord.y;
    float d = 1 - x*x - y*y;
    if (d <= 0)
        discard;

    float z = sqrt(d);
    vec3 normal = vec3(x, y, z);

    // Diffuse color
    float diffuse = dot(v_light_direction, normal);
    // clamp, because 0 < theta < pi/2
    diffuse = clamp(diffuse, 0, 1);
    vec3 diffuse_color = u_light_ambient + u_light_color * diffuse;

    // Specular color
    //   reflect light wrt normal for the reflected ray, then
    //   find the angle made with the eye
    vec3 eye = vec3(0, 0, -1);
    float specular = dot(reflect(v_light_direction, normal), eye);
    specular = clamp(specular, 0, 1);
    // raise to the material's shininess, multiply with a
    // small factor for spread
    specular = pow(specular, 80);
    vec3 specular_color = u_light_color * specular;

    gl_FragColor = vec4(v_color.rgb * diffuse_color + specular_color, v_color.a * u_alpha);

    gl_FragDepth = gl_FragCoord.z - 0.5 * z * v_depth_middle;
}
"""


class PseudoSpheresVisual(Visual):
    """Visual displaying marker symbols."""

    def __init__(self, light_color='white', light_position=(1, -1, 1),
                 light_ambient=0.3, alpha=1, **kwargs):
        self._vbo = VertexBuffer()
        self._data = None

        Visual.__init__(self, vcode=vert, fcode=frag)

        self.light_color = light_color
        self.light_position = light_position
        self.light_ambient = light_ambient
        self.alpha = alpha

        self._draw_mode = 'points'
        self.set_gl_state('translucent', depth_test=True, cull_face=True)

        if len(kwargs) > 0:
            self.set_data(**kwargs)

        self.freeze()

    def set_data(self, pos=None, radius=10, color='white'):
        """Set the data used to display this visual.

        Parameters
        ----------
        pos : array
            The array of locations to display each sphere.
        radius : float or array
            The sphere radii in px.
        color : Color | ColorArray
            The color used to draw each sphere.
        """
        if pos is not None:
            assert (isinstance(pos, np.ndarray) and
                    pos.ndim == 2 and pos.shape[1] in (2, 3))

            n = len(pos)
            data = np.zeros(n, dtype=[('a_position', np.float32, 3),
                                      ('a_color', np.float32, 4),
                                      ('a_radius', np.float32)])

            data['a_position'][:, :pos.shape[1]] = pos
            if len(color) == 1:
                color = color[0]
            data['a_color'] = ColorArray(color).rgba
            data['a_radius'] = radius

            self._data = data
            self._vbo.set_data(data)
            self.shared_program.bind(self._vbo)

        self.update()

    @property
    def light_position(self):
        return self._light_position

    @light_position.setter
    def light_position(self, value):
        self.shared_program['u_light_position'] = value
        self._light_position = value
        self.update()

    @property
    def light_ambient(self):
        return self._light_ambient

    @light_ambient.setter
    def light_ambient(self, value):
        self.shared_program['u_light_ambient'] = value
        self._light_ambient = value
        self.update()

    @property
    def light_color(self):
        return self._light_color

    @light_color.setter
    def light_color(self, value):
        self.shared_program['u_light_color'] = ColorArray(value).rgb
        self._light_color = value
        self.update()

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        self.shared_program['u_alpha'] = value
        self._alpha = value
        self.update()

    def _prepare_transforms(self, view):
        view.view_program.vert['visual_to_framebuffer'] = view.get_transform('visual', 'framebuffer')
        view.view_program.vert['framebuffer_to_visual'] = view.get_transform('framebuffer', 'visual')
        view.view_program.vert['framebuffer_to_render'] = view.get_transform('framebuffer', 'render')

    def _compute_bounds(self, axis, view):
        pos = self._data['a_position']
        if pos is None:
            return None
        if pos.shape[1] > axis:
            return (pos[:, axis].min(), pos[:, axis].max())
        else:
            return (0, 0)
