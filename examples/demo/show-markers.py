#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 2

""" Display markers at different sizes and line thicknessess.
"""

import os
import sys

import numpy as np
from vispy.gloo import gl

from vispy import app
from vispy.util.transforms import ortho
from vispy.gloo import Program
from vispy.gloo import VertexBuffer

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
        app.Canvas.__init__(self)

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
            program.set_vars(self.vbo,
                             u_antialias=u_antialias,
                             u_size=1,
                             u_model=self.model,
                             u_view=self.view,
                             u_projection=self.projection)
        self.index = 0
        self.program = self.programs[self.index]

    def on_initialize(self, event):
        gl.glClearColor(1, 1, 1, 1)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def on_key_press(self, event):
        if event.text == ' ':
            self.index = (self.index + 1) % (len(self.programs))
            self.program = self.programs[self.index]
            self.program['u_projection'] = self.projection
            self.program['u_size'] = self.u_size
            self.update()

    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)
        self.projection = ortho(0, width, 0, height, -100, 100)
        self.u_size = width / 512.0
        self.program['u_projection'] = self.projection
        self.program['u_size'] = self.u_size

    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.program.draw(gl.GL_POINTS)

if __name__ == '__main__':
    canvas = Canvas()
    canvas.show()
    app.run()
