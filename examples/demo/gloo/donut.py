# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Nicolas P .Rougier
# Date:   04/03/2014
# -----------------------------------------------------------------------------
"""
Mesmerizing donut
"""

import numpy as np
from vispy import gloo
from vispy import app
from vispy.util.transforms import perspective, translate, rotate

vert = """
#version 120

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform float u_linewidth;
uniform float u_antialias;
uniform float u_size;
uniform float u_clock;

attribute vec2  a_position;
attribute vec4  a_fg_color;
attribute vec4  a_bg_color;
attribute float a_size;

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_size;
varying float v_linewidth;
varying float v_antialias;

void main (void) {
    v_size = a_size * u_size;
    v_linewidth = u_linewidth;
    v_antialias = u_antialias;
    v_fg_color  = a_fg_color;
    v_bg_color  = a_bg_color;

    float x0 = 0.5;
    float z0 = 0.0;

    float theta = a_position.x + u_clock;
    float x1 = x0*cos(theta) + z0*sin(theta) - 1.0;
    float y1 = 0.0;
    float z1 = z0*cos(theta) - x0*sin(theta);

    float phi = a_position.y;
    float x2 = x1*cos(phi) + y1*sin(phi);
    float y2 = y1*cos(phi) - x1*sin(phi);
    float z2 = z1;

    gl_Position = u_projection * u_view * u_model * vec4(x2,y2,z2,1.);
    gl_PointSize = v_size + 2.*(v_linewidth + 1.5*v_antialias);
}
"""

frag = """
#version 120

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_size;
varying float v_linewidth;
varying float v_antialias;
void main()
{
    float size = v_size +2*(v_linewidth + 1.5*v_antialias);
    float t = v_linewidth/2.0-v_antialias;
    float r = length((gl_PointCoord.xy - vec2(0.5,0.5))*size) - v_size/2.;
    float d = abs(r) - t;
    if( r > (v_linewidth/2.0+v_antialias))
    {
        discard;
    }
    else if( d < 0.0 )
    {
       gl_FragColor = v_fg_color;
    }
    else
    {
        float alpha = d/v_antialias;
        alpha = exp(-alpha*alpha);
        if (r > 0)
            gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
        else
            gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
    }
}
"""


# ------------------------------------------------------------ Canvas class ---
class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=(800, 800))
        ps = self.pixel_scale

        self.title = "D'oh! A big donut"

        # Create vertices
        n, p = 50, 40
        data = np.zeros(p * n, [('a_position', np.float32, 2),
                                ('a_bg_color', np.float32, 4),
                                ('a_fg_color', np.float32, 4),
                                ('a_size', np.float32)])
        data['a_position'][:, 0] = np.resize(np.linspace(
                                             0, 2 * np.pi, n), p * n)
        data['a_position'][:, 1] = np.repeat(np.linspace(0, 2 * np.pi, p), n)
        data['a_bg_color'] = np.random.uniform(0.75, 1.00, (n * p, 4))
        data['a_bg_color'][:, 3] = 1
        data['a_fg_color'] = 0, 0, 0, 1
        # data['a_size'] = np.random.uniform(8*ps, 8*ps, n * p)
        data['a_size'] = 8.0*ps
        u_linewidth = 1.0*ps
        u_antialias = 1.0

        self.translate = 5
        self.program = gloo.Program(vert, frag)
        self.view = translate((0, 0, -self.translate))
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        self.program.bind(gloo.VertexBuffer(data))
        self.program['u_linewidth'] = u_linewidth
        self.program['u_antialias'] = u_antialias
        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        self.program['u_size'] = 5 / self.translate

        self.apply_zoom()

        self.theta = 0
        self.phi = 0
        self.clock = 0
        self.stop_rotation = False

        gloo.set_state('translucent', clear_color='white')
        self.program['u_clock'] = 0.0

        self._timer = app.Timer('auto', connect=self.on_timer, start=True)

        self.show()

    def on_key_press(self, event):
        if event.text == ' ':
            self.stop_rotation = not self.stop_rotation

    def on_timer(self, event):
        if not self.stop_rotation:
            self.theta += .5
            self.phi += .5
            self.model = np.dot(rotate(self.theta, (0, 0, 1)),
                                rotate(self.phi, (0, 1, 0)))
            self.program['u_model'] = self.model
        self.clock += np.pi / 1000
        self.program['u_clock'] = self.clock
        self.update()

    def on_resize(self, event):
        self.apply_zoom()

    def on_mouse_wheel(self, event):
        self.translate -= event.delta[1]
        self.translate = max(2, self.translate)
        self.view = translate((0, 0, -self.translate))

        self.program['u_view'] = self.view
        self.program['u_size'] = 5 / self.translate
        self.update()

    def on_draw(self, event):
        gloo.clear()
        self.program.draw('points')

    def apply_zoom(self):
        gloo.set_viewport(0, 0, self.physical_size[0], self.physical_size[1])
        self.projection = perspective(45.0, self.size[0] /
                                      float(self.size[1]), 1.0, 1000.0)
        self.program['u_projection'] = self.projection


if __name__ == '__main__':
    c = Canvas()
    app.run()
