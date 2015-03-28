# !/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 2
""" Simple example plotting 2D points.
"""

from vispy import gloo
from vispy import app
import numpy as np

VERT_SHADER = """
attribute vec2  a_position;
attribute vec3  a_color;
attribute float a_size;

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_radius;
varying float v_linewidth;
varying float v_antialias;

void main (void) {
    v_radius = a_size;
    v_linewidth = 1.0;
    v_antialias = 1.0;
    v_fg_color  = vec4(0.0,0.0,0.0,0.5);
    v_bg_color  = vec4(a_color,    1.0);

    gl_Position = vec4(a_position, 0.0, 1.0);
    gl_PointSize = 2.0*(v_radius + v_linewidth + 1.5*v_antialias);
}
"""

FRAG_SHADER = """
#version 120

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_radius;
varying float v_linewidth;
varying float v_antialias;
void main()
{
    float size = 2.0*(v_radius + v_linewidth + 1.5*v_antialias);
    float t = v_linewidth/2.0-v_antialias;
    float r = length((gl_PointCoord.xy - vec2(0.5,0.5))*size);
    float d = abs(r - v_radius) - t;
    if( d < 0.0 )
        gl_FragColor = v_fg_color;
    else
    {
        float alpha = d/v_antialias;
        alpha = exp(-alpha*alpha);
        if (r > v_radius)
            gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
        else
            gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
    }
}
"""


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive')
        ps = self.pixel_scale

        # Create vertices
        n = 10000
        v_position = 0.25 * np.random.randn(n, 2).astype(np.float32)
        v_color = np.random.uniform(0, 1, (n, 3)).astype(np.float32)
        v_size = np.random.uniform(2*ps, 12*ps, (n, 1)).astype(np.float32)

        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        # Set uniform and attribute
        self.program['a_color'] = gloo.VertexBuffer(v_color)
        self.program['a_position'] = gloo.VertexBuffer(v_position)
        self.program['a_size'] = gloo.VertexBuffer(v_size)
        gloo.set_state(clear_color='white', blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

        self.show()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.physical_size)

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        self.program.draw('points')


if __name__ == '__main__':
    c = Canvas()
    app.run()
