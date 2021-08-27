# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""Pseudo spheres (shaded discs) visual"""

import numpy as np

from ..color import ColorArray
from ..gloo import VertexBuffer, _check_valid
from .shaders import Function, Variable
from .visual import Visual


vert = """
uniform float u_antialias;
uniform vec3 u_light_position;
uniform float u_scale;
uniform float u_px_scale;

attribute vec3 a_position;
attribute vec4 a_color;
attribute float a_size;

varying vec4 v_color;
varying float v_size;
varying vec3 v_light_direction;
varying float v_antialias;
varying float v_depth;
varying float v_depth_size;

void main (void) {
    v_antialias = u_antialias;
    v_color = a_color;
    v_size = a_size * u_scale * u_px_scale;

    vec4 pos = vec4(a_position, 1.0);
    vec4 fb_pos = $visual_to_framebuffer(pos);
    gl_Position = $framebuffer_to_render(fb_pos);


    // Measure the orientation of the framebuffer coordinate system relative
    // to the atom
    vec4 x = $framebuffer_to_visual(fb_pos + vec4(100, 0, 0, 0));
    x = (x/x.w - pos) / 100;
    vec4 z = $framebuffer_to_visual(fb_pos + vec4(0, 0, -100, 0));
    z = (z/z.w - pos) / 100;

    v_depth = gl_Position.z / gl_Position.w;
    vec4 depth_z = $framebuffer_to_render($visual_to_framebuffer(pos + normalize(z) * a_size));
    v_depth_size = v_depth - depth_z.z / depth_z.w;

    v_light_direction = normalize(u_light_position);
    gl_PointSize = v_size + (6 * v_antialias);
}
"""


frag = """
varying vec4 v_color;
varying float v_size;
varying vec3 v_light_direction;
varying float v_antialias;
varying float v_depth;
varying float v_depth_radius;

void main()
{
    // discard size 0 spheres
    if (v_size <= 0.)
        discard;

    float frag_dist = length(gl_PointCoord.xy - vec2(0.5, 0.5));

    float aliased_size = v_size + (6 * v_antialias);
    float scaled_antialias = v_antialias / aliased_size;

    if (frag_dist > 0.5 + scaled_antialias/2)
        discard;

    float alpha = 1.0;
    if (frag_dist >= 0.5 - scaled_antialias/2) {
        float alias_amount = (frag_dist - 0.5 + scaled_antialias/2) / scaled_antialias;
        alpha = exp(-alias_amount*alias_amount);
    }

//    vec3 normal = normalize(vec3(p.xy, z));
//    vec3 direction = normalize(vec3(1.0, 1.0, 1.0));
//    float diffuse = max(0.0, dot(direction, normal));
//    float specular = pow(diffuse, 24.0);
//    gl_FragColor = vec4(max(diffuse*v_color.xyz, specular*vec3(1.0)), 1.0);

    gl_FragColor = vec4(v_color.rgb, v_color.a * alpha);
    gl_FragDepth = v_depth - .5 * (1 - ) * v_depth_radius;
}
"""


class PseudoSpheresVisual(Visual):
    """Visual displaying marker symbols."""

    def __init__(self, **kwargs):
        self._vbo = VertexBuffer()
        self._data = None
        self.antialias = 1

        Visual.__init__(self, vcode=vert, fcode=frag)

        self._draw_mode = 'points'
        self.set_gl_state('translucent', depth_test=True, cull_face=True)

        if len(kwargs) > 0:
            self.set_data(**kwargs)

        self.freeze()

    def set_data(self, pos=None, size=10., color='white'):
        """Set the data used to display this visual.

        Parameters
        ----------
        pos : array
            The array of locations to display each symbol.
        symbol : str
            The style of symbol to draw (see Notes).
        size : float or array
            The symbol size in px.
        color : Color | ColorArray
            The color used to draw each symbol outline.

        Notes
        -----
        Allowed style strings are: disc, arrow, ring, clobber, square, diamond,
        vbar, hbar, cross, tailed_arrow, x, triangle_up, triangle_down,
        and star.
        """
        if pos is not None:
            assert (isinstance(pos, np.ndarray) and
                    pos.ndim == 2 and pos.shape[1] in (2, 3))

            n = len(pos)
            data = np.zeros(n, dtype=[('a_position', np.float32, 3),
                                      ('a_color', np.float32, 4),
                                      ('a_size', np.float32)])

            data['a_position'][:, :pos.shape[1]] = pos
            if len(color) == 1:
                color = color[0]
            data['a_color'] = ColorArray(color).rgba
            data['a_size'] = size
            self.shared_program['u_antialias'] = self.antialias
            self._data = data
            self._vbo.set_data(data)
            self.shared_program.bind(self._vbo)

        self.update()

    def _prepare_draw(self, view):
        view.view_program['u_px_scale'] = view.transforms.pixel_scale
        tr = view.transforms.get_transform('visual', 'document').simplified
        mat = tr.map(np.eye(3)) - tr.map(np.zeros((3, 3)))
        scale = np.linalg.norm(mat[:, :3])
        view.view_program['u_scale'] = scale

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
