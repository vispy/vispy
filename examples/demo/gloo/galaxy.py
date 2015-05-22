#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 30
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Just a very fake galaxy.
Astronomers and cosmologists will kill me !
"""

import numpy as np

from vispy import gloo
from vispy import app
from vispy.util.transforms import perspective, translate, rotate

# Manual galaxy creation
# (did you really expect a simulation in less than 250 python lines ?)


def make_arm(n, angle):
    R = np.linspace(10, 450 + 50 * np.random.uniform(.5, 1.), n)
    R += 40 * np.random.normal(0, 2., n) * np.linspace(1, .1, n)
    T = angle + np.linspace(0, 2.5 * np.pi, n) + \
        np.pi / 6 * np.random.normal(0, .5, n)
    S = 8 + 2 * np.abs(np.random.normal(0, 1, n))
    S *= np.linspace(1, .85, n)
    P = np.zeros((n, 3), dtype=np.float32)
    X, Y, Z = P[:, 0], P[:, 1], P[:, 2]
    X[...] = R * np.cos(T)
    Y[...] = R * np.sin(T) * 1.1
    D = np.sqrt(X * X + Y * Y)
    Z[...] = 8 * np.random.normal(0, 2 - D / 512., n)
    X += (D * np.random.uniform(0, 1, n) > 250) * \
        (.05 * D * np.random.uniform(-1, 1, n))
    Y += (D * np.random.uniform(0, 1, n) > 250) * \
        (.05 * D * np.random.uniform(-1, 1, n))
    Z += (D * np.random.uniform(0, 1, n) > 250) * \
        (.05 * D * np.random.uniform(-1, 1, n))
    D = (D - D.min()) / (D.max() - D.min())

    return P / 256, S / 2, D
p = 50000
n = 3 * p

# Very simple colormap
cmap = np.array([[255, 124, 0], [255, 163, 76],
                 [255, 192, 130], [255, 214, 173],
                 [255, 232, 212], [246, 238, 237],
                 [237, 240, 253], [217, 228, 255],
                 [202, 219, 255], [191, 212, 255],
                 [182, 206, 255], [174, 202, 255],
                 [168, 198, 255], [162, 195, 255],
                 [158, 192, 255], [155, 189, 255],
                 [151, 187, 255], [148, 185, 255],
                 [145, 183, 255], [143, 182, 255],
                 [141, 181, 255], [140, 179, 255],
                 [139, 179, 255],
                 [137, 177, 255]], dtype=np.uint8).reshape(1, 24, 3)


VERT_SHADER = """
#version 120
// Uniforms
// ------------------------------------
uniform mat4  u_model;
uniform mat4  u_view;
uniform mat4  u_projection;
uniform float u_size;


// Attributes
// ------------------------------------
attribute vec3  a_position;
attribute float a_size;
attribute float a_dist;

// Varyings
// ------------------------------------
varying float v_size;
varying float v_dist;

void main (void) {
    v_size  = a_size*u_size*.75;
    v_dist  = a_dist;
    gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
    gl_PointSize = v_size;
}
"""

FRAG_SHADER = """
#version 120
// Uniforms
// ------------------------------------
uniform sampler2D u_colormap;

// Varyings
// ------------------------------------
varying float v_size;
varying float v_dist;

// Main
// ------------------------------------
void main()
{
    float a = 2*(length(gl_PointCoord.xy - vec2(0.5,0.5)) / sqrt(2.0));
    vec3 color = texture2D(u_colormap, vec2(v_dist,.5)).rgb;
    gl_FragColor = vec4(color,(1-a)*.25);
}
"""


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=(800, 600))
        ps = self.pixel_scale

        self.title = "A very fake galaxy [mouse scroll to zoom]"

        data = np.zeros(n, [('a_position', np.float32, 3),
                        ('a_size', np.float32, 1),
                        ('a_dist', np.float32, 1)])

        for i in range(3):
            P, S, D = make_arm(p, i * 2 * np.pi / 3)
            data['a_dist'][(i + 0) * p:(i + 1) * p] = D
            data['a_position'][(i + 0) * p:(i + 1) * p] = P
            data['a_size'][(i + 0) * p:(i + 1) * p] = S*ps

        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)
        self.theta, self.phi = 0, 0

        self.translate = 5
        self.view = translate((0, 0, -self.translate))

        self.program.bind(gloo.VertexBuffer(data))
        self.program['u_colormap'] = gloo.Texture2D(cmap)
        self.program['u_size'] = 5. / self.translate
        self.program['u_model'] = self.model
        self.program['u_view'] = self.view

        self.apply_zoom()

        gloo.set_state(depth_test=False, blend=True,
                       blend_func=('src_alpha', 'one'), clear_color='black')

        # Start the timer upon initialization.
        self.timer = app.Timer('auto', connect=self.on_timer)
        self.timer.start()

        self.show()

    def on_key_press(self, event):
        if event.text == ' ':
            if self.timer.running:
                self.timer.stop()
            else:
                self.timer.start()

    def on_timer(self, event):
        self.theta += .11
        self.phi += .13
        self.model = np.dot(rotate(self.theta, (0, 0, 1)),
                            rotate(self.phi, (0, 1, 0)))
        self.program['u_model'] = self.model
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
