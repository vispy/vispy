# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author:   Nicolas P .Rougier
# Date:     06/03/2014
# Abstract: Water ripple effect following mouse
# Keywords: antialias, water, mouse
# -----------------------------------------------------------------------------

import numpy as np

from vispy import gloo, app
from vispy.gloo import Program, VertexBuffer
from vispy.util.transforms import ortho

vertex = """
#version 120

uniform mat4  u_model;
uniform mat4  u_view;
uniform mat4  u_projection;
uniform float u_linewidth;
uniform float u_antialias;

attribute vec3  a_position;
attribute vec4  a_fg_color;
attribute float a_size;

varying vec4  v_fg_color;
varying float v_size;

void main (void)
{
    v_size = a_size;
    v_fg_color = a_fg_color;
    if( a_fg_color.a > 0.0)
    {
        gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
        gl_PointSize = v_size + u_linewidth + 2*1.5*u_antialias;
    }
    else
    {
        gl_Position = u_projection * u_view * u_model * vec4(-1,-1,0,1);
        gl_PointSize = 0.0;
    }
}
"""

fragment = """
#version 120

uniform float u_linewidth;
uniform float u_antialias;
varying vec4  v_fg_color;
varying vec4  v_bg_color;
varying float v_size;
float disc(vec2 P, float size)
{
    return length((P.xy - vec2(0.5,0.5))*size);
}
void main()
{
    if( v_fg_color.a <= 0.0)
        discard;
    float actual_size = v_size + u_linewidth + 2*1.5*u_antialias;
    float t = u_linewidth/2.0 - u_antialias;
    float r = disc(gl_PointCoord, actual_size);
    float d = abs(r - v_size/2.0) - t;
    if( d < 0.0 )
    {
         gl_FragColor = v_fg_color;
    }
    else if( abs(d) > 2.5*u_antialias )
    {
         discard;
    }
    else
    {
        d /= u_antialias;
        gl_FragColor = vec4(v_fg_color.rgb, exp(-d*d)*v_fg_color.a);
    }
}
"""


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, title='Rain [Move mouse]',
                            size=(512, 512), keys='interactive')

        # Build data
        # --------------------------------------
        n = 500
        self.data = np.zeros(n, [('a_position', np.float32, 2),
                                 ('a_fg_color', np.float32, 4),
                                 ('a_size',     np.float32, 1)])
        self.index = 0
        self.program = Program(vertex, fragment)
        self.vdata = VertexBuffer(self.data)
        self.program.bind(self.vdata)
        self.program['u_antialias'] = 1.00
        self.program['u_linewidth'] = 1.00
        self.program['u_model'] = np.eye(4, dtype=np.float32)
        self.program['u_view'] = np.eye(4, dtype=np.float32)

        self.activate_zoom()

        gloo.set_clear_color('white')
        gloo.set_state(blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))
        self.timer = app.Timer('auto', self.on_timer, start=True)

        self.show()

    def on_draw(self, event):
        gloo.clear()
        self.program.draw('points')

    def on_resize(self, event):
        self.activate_zoom()

    def activate_zoom(self):
        gloo.set_viewport(0, 0, *self.physical_size)
        projection = ortho(0, self.size[0], 0,
                           self.size[1], -1, +1)
        self.program['u_projection'] = projection

    def on_timer(self, event):
        self.data['a_fg_color'][..., 3] -= 0.01
        self.data['a_size'] += 1.0
        self.vdata.set_data(self.data)
        self.update()

    def on_mouse_move(self, event):
        x, y = event.pos
        h = self.size[1]
        self.data['a_position'][self.index] = x, h - y
        self.data['a_size'][self.index] = 5
        self.data['a_fg_color'][self.index] = 0, 0, 0, 1
        self.index = (self.index + 1) % 500


if __name__ == '__main__':
    canvas = Canvas()
    app.run()
