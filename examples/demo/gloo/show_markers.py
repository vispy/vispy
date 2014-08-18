#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 2

""" Display markers at different sizes and line thicknessess.
"""

import os
import sys

import numpy as np

from vispy import app
from vispy.util.transforms import ortho
from vispy.gloo import Program, VertexBuffer
from vispy import gloo

sys.path.insert(0, os.path.dirname(__file__))
import markers


n = 540
data = np.zeros(n, dtype=[('a_position', np.float32, 3),
                          ('a_fg_color', np.float32, 4),
                          ('a_bg_color', np.float32, 4),
                          ('a_size', np.float32, 1),
                          ('a_linewidth', np.float32, 1)])
data['a_fg_color'] = 0, 0, 0, 1
data['a_bg_color'] = 1, 1, 1, 1
data['a_linewidth'] = 1
u_antialias = 1

radius, theta, dtheta = 255.0, 0.0, 5.5 / 180.0 * np.pi
for i in range(500):
    theta += dtheta
    x = 256 + radius * np.cos(theta)
    y = 256 + 32 + radius * np.sin(theta)
    r = 10.1 - i * 0.02
    radius -= 0.45
    data['a_position'][i] = x, y, 0
    data['a_size'][i] = 2 * r

for i in range(40):
    r = 4
    thickness = (i + 1) / 10.0
    x = 20 + i * 12.5 - 2 * r
    y = 16
    data['a_position'][500 + i] = x, y, 0
    data['a_size'][500 + i] = 2 * r
    data['a_linewidth'][500 + i] = thickness


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive')

        # This size is used for comparison with agg (via matplotlib)
        self.size = 512, 512 + 2 * 32
        self.title = "Markers demo [press space to change marker]"

        self.vbo = VertexBuffer(data)
        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = ortho(0, self.size[0], 0, self.size[1], -1, 1)
        self.programs = [
            Program(markers.vert, markers.frag + markers.tailed_arrow),
            Program(markers.vert, markers.frag + markers.disc),
            Program(markers.vert, markers.frag + markers.diamond),
            Program(markers.vert, markers.frag + markers.square),
            Program(markers.vert, markers.frag + markers.cross),
            Program(markers.vert, markers.frag + markers.arrow),
            Program(markers.vert, markers.frag + markers.vbar),
            Program(markers.vert, markers.frag + markers.hbar),
            Program(markers.vert, markers.frag + markers.clobber),
            Program(markers.vert, markers.frag + markers.ring)]

        for program in self.programs:
            program.bind(self.vbo)
            program["u_antialias"] = u_antialias,
            program["u_size"] = 1
            program["u_model"] = self.model
            program["u_view"] = self.view
            program["u_projection"] = self.projection
        self.index = 0
        self.program = self.programs[self.index]

    def on_initialize(self, event):
        gloo.set_state(depth_test=False, blend=True, clear_color='white',
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

    def on_key_press(self, event):
        if event.text == ' ':
            self.index = (self.index + 1) % (len(self.programs))
            self.program = self.programs[self.index]
            self.program['u_projection'] = self.projection
            self.program['u_size'] = self.u_size
            self.update()

    def on_resize(self, event):
        width, height = event.size
        gloo.set_viewport(0, 0, width, height)
        self.projection = ortho(0, width, 0, height, -100, 100)
        self.u_size = width / 512.0
        self.program['u_projection'] = self.projection
        self.program['u_size'] = self.u_size

    def on_draw(self, event):
        gloo.clear()
        self.program.draw('points')

if __name__ == '__main__':
    canvas = Canvas()
    canvas.show()
    app.run()
