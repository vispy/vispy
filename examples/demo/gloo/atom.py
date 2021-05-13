# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Nicolas P .Rougier
# Date:   06/03/2014
# Abstract: Fake electrons orbiting
# Keywords: Sprites, atom, particles
# -----------------------------------------------------------------------------

import numpy as np
from vispy import gloo
from vispy import app
from vispy.util.transforms import perspective, translate, rotate

# Create vertices
n, p = 100, 150
data = np.zeros(p * n, [('a_position', np.float32, 2),
                        ('a_color', np.float32, 4),
                        ('a_rotation', np.float32, 4)])
trail = .5 * np.pi
data['a_position'][:, 0] = np.resize(np.linspace(0, trail, n), p * n)
data['a_position'][:, 0] += np.repeat(np.random.uniform(0, 2 * np.pi, p), n)
data['a_position'][:, 1] = np.repeat(np.linspace(0, 2 * np.pi, p), n)

data['a_color'] = 1, 1, 1, 1
data['a_color'] = np.repeat(
    np.random.uniform(0.75, 1.00, (p, 4)).astype(np.float32), n, axis=0)
data['a_color'][:, 3] = np.resize(np.linspace(0, 1, n), p * n)

data['a_rotation'] = np.repeat(
    np.random.uniform(0, 2 * np.pi, (p, 4)).astype(np.float32), n, axis=0)


vert = """
#version 120
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform float u_size;
uniform float u_clock;

attribute vec2 a_position;
attribute vec4 a_color;
attribute vec4 a_rotation;
varying vec4 v_color;

mat4 build_rotation(vec3 axis, float angle)
{
    axis = normalize(axis);
    float s = sin(angle);
    float c = cos(angle);
    float oc = 1.0 - c;
    return mat4(oc * axis.x * axis.x + c,
                oc * axis.x * axis.y - axis.z * s,
                oc * axis.z * axis.x + axis.y * s,
                0.0,
                oc * axis.x * axis.y + axis.z * s,
                oc * axis.y * axis.y + c,
                oc * axis.y * axis.z - axis.x * s,
                0.0,
                oc * axis.z * axis.x - axis.y * s,
                oc * axis.y * axis.z + axis.x * s,
                oc * axis.z * axis.z + c,
                0.0,
                0.0, 0.0, 0.0, 1.0);
}


void main (void) {
    v_color = a_color;

    float x0 = 1.5;
    float z0 = 0.0;

    float theta = a_position.x + u_clock;
    float x1 = x0*cos(theta) + z0*sin(theta);
    float y1 = 0.0;
    float z1 = (z0*cos(theta) - x0*sin(theta))/2.0;

    mat4 R = build_rotation(a_rotation.xyz, a_rotation.w);
    gl_Position = u_projection * u_view * u_model * R * vec4(x1,y1,z1,1);
    gl_PointSize = 8.0 * u_size * sqrt(v_color.a);
}
"""

frag = """
#version 120
varying vec4 v_color;
varying float v_size;
void main()
{
    float d = 2*(length(gl_PointCoord.xy - vec2(0.5,0.5)));
    gl_FragColor = vec4(v_color.rgb, v_color.a*(1-d));
}
"""


# ------------------------------------------------------------ Canvas class ---
class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=(800, 800))
        self.title = "Atom [zoom with mouse scroll]"

        self.translate = 6.5
        self.program = gloo.Program(vert, frag)
        self.view = translate((0, 0, -self.translate))
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)
        self.apply_zoom()

        self.program.bind(gloo.VertexBuffer(data))
        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        self.program['u_size'] = 5 / self.translate

        self.theta = 0
        self.phi = 0
        self.clock = 0
        self.stop_rotation = False

        gloo.set_state('translucent', depth_test=False)
        self.program['u_clock'] = 0.0

        self._timer = app.Timer('auto', connect=self.on_timer, start=True)

        self.show()

    def on_key_press(self, event):
        if event.text == ' ':
            self.stop_rotation = not self.stop_rotation

    def on_timer(self, event):
        if not self.stop_rotation:
            self.theta += .05
            self.phi += .05
            self.model = np.dot(rotate(self.theta, (0, 0, 1)),
                                rotate(self.phi, (0, 1, 0)))
            self.program['u_model'] = self.model
        self.clock += np.pi / 100
        self.program['u_clock'] = self.clock
        self.update()

    def on_resize(self, event):
        self.apply_zoom()

    def on_mouse_wheel(self, event):
        self.translate += event.delta[1]
        self.translate = max(2, self.translate)
        self.view = translate((0, 0, -self.translate))
        self.program['u_view'] = self.view
        self.program['u_size'] = 5 / self.translate
        self.update()

    def on_draw(self, event):
        gloo.clear('black')
        self.program.draw('points')

    def apply_zoom(self):
        width, height = self.physical_size
        gloo.set_viewport(0, 0, width, height)
        self.projection = perspective(45.0, width / float(height), 1.0, 1000.0)
        self.program['u_projection'] = self.projection


if __name__ == '__main__':
    c = Canvas()
    app.run()
