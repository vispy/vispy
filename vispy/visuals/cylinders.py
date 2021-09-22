# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""Cylinders Visual and shader definitions."""

import numpy as np

from ..color import ColorArray
from ..gloo import VertexBuffer
from .visual import Visual


vert = """
attribute vec3 a_position;
attribute float a_width;
attribute vec4 a_color;

varying vec4 v_color;
varying float v_width;

float big_float = 1e10; // prevents numerical imprecision

void main (void) {
    v_color = a_color;

    vec4 pos = vec4(a_position, 1);
    vec4 fb_pos = $visual_to_framebuffer(pos);
    gl_Position = $framebuffer_to_render(fb_pos);

    // calculate point size from visual to framebuffer coords to determine size
    vec4 x = $framebuffer_to_visual(fb_pos + vec4(big_float, 0, 0, 0));
    x = (x - pos);
    vec4 size_vec = $visual_to_framebuffer(pos + normalize(x) * a_width);
    v_width = size_vec.x / size_vec.w - fb_pos.x / fb_pos.w;
}
"""


geom = """
#version 450
layout (lines) in;
layout (triangle_strip, max_vertices=4) out;

in vec4 v_color[];
in float v_width[];

out vec4 v_color_out;

void main(void) {
    vec4 start = gl_in[0].gl_Position;
    vec4 end = gl_in[1].gl_Position;
    vec4 direction = normalize(start - end);
    vec4 perp1 = vec4(vec2(direction.y, -direction.x), 0, 0);
    vec4 perp2 = vec4(vec2(-direction.y, direction.x), 0, 0);
    gl_Position = start + perp1 * v_width[0];
    v_color_out = v_color[0];
    EmitVertex();
    gl_Position = start + perp2 * v_width[0];
    v_color_out = v_color[0];
    EmitVertex();
    gl_Position = end + perp1 * v_width[1];
    v_color_out = v_color[1];
    EmitVertex();
    gl_Position = end + perp2 * v_width[1];
    v_color_out = v_color[1];
    EmitVertex();
    EndPrimitive();
}
"""

frag = """
varying vec4 v_color_out;

void main()
{
    gl_FragColor = vec4(v_color_out);
}
"""

class CylindersVisual(Visual):
    """Visual displaying marker symbols.

    Parameters
    ----------
    pos : array
        The array of locations to display each symbol.
    size : float or array
        The symbol size in screen (or data, if scaling is on) px.
    edge_width : float or array or None
        The width of the symbol outline in screen (or data, if scaling is on) px.
    edge_width_rel : float or array or None
        The width as a fraction of marker size. Exactly one of
        `edge_width` and `edge_width_rel` must be supplied.
    edge_color : Color | ColorArray
        The color used to draw each symbol outline.
    face_color : Color | ColorArray
        The color used to draw each symbol interior.
    symbol : str
        The style of symbol to draw (see Notes).
    scaling : bool
        If set to True, marker scales when rezooming.
    alpha : float
        The opacity level of the visual.
    antialias : float
        Antialiasing amount (in px).
    spherical : bool
        Whether to add a spherical effect on the marker using lighting.
    light_color : Color | ColorArray
        The color of the light used to create the spherical effect.
    light_position : array
        The coordinates of the light used to create the spherical effect.
    light_ambient : float
        The amount of ambient light used to create the spherical effect.

    Notes
    -----
    Allowed style strings are: disc, arrow, ring, clobber, square, diamond,
    vbar, hbar, cross, tailed_arrow, x, triangle_up, triangle_down,
    and star.
    """
    def __init__(self, **kwargs):
        self._vbo = VertexBuffer()
        self._data = None

        Visual.__init__(self, vcode=vert, gcode=geom, fcode=frag)

        self.set_gl_state(depth_test=True, blend=True,
                          blend_func=('src_alpha', 'one_minus_src_alpha'))
        self._draw_mode = 'lines'

        if len(kwargs) > 0:
            self.set_data(**kwargs)

        self.freeze()

    def set_data(self, pos=None, width=1, color='white'):
        color = ColorArray(color).rgba
        if len(color) == 1:
            color = color[0]

        if pos is not None:
            assert (isinstance(pos, np.ndarray) and
                    pos.ndim == 2 and pos.shape[1] in (2, 3))

            n = len(pos)
            data = np.zeros(n, dtype=[('a_position', np.float32, 3),
                                      ('a_color', np.float32, 4),
                                      ('a_width', np.float32),
                                      ])
            data['a_color'] = color
            data['a_width'] = width
            data['a_position'] = pos
            self._data = data
            self._vbo.set_data(data)
            self.shared_program.bind(self._vbo)

        self.update()

    def _prepare_transforms(self, view):
        view.view_program.vert['visual_to_framebuffer'] = view.get_transform('visual', 'framebuffer')
        view.view_program.vert['framebuffer_to_render'] = view.get_transform('framebuffer', 'render')
        view.view_program.vert['framebuffer_to_visual'] = view.get_transform('framebuffer', 'visual')
        # view.view_program.geom['render_to_framebuffer'] = view.get_transform('render', 'visual')
        # view.view_program.geom['visual_to_framebuffer'] = view.get_transform('visual', 'framebuffer')
