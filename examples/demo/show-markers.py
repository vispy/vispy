# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# VisPy - Copyright (c) 2013, Vispy Development Team All rights reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" Display markers at different sizes and line thicknessess. """
import numpy as np
from vispy import gl
from OpenGL import GL

from vispy import app
from vispy.util.transforms import ortho
from vispy.oogl import Program
from vispy.oogl import VertexBuffer
import markers


n = 540
data = np.zeros(n, dtype = [ ('a_position', np.float32, 3),
                             ('a_fg_color', np.float32, 4),
                             ('a_bg_color', np.float32, 4),
                             ('a_size',     np.float32, 1),
                             ('a_linewidth',np.float32, 1) ])
data['a_fg_color']  = 0,0,0,1
data['a_bg_color']  = 1,1,1,1
data['a_linewidth'] = 1
u_antialias = 1

radius, theta, dtheta = 255.0, 0.0, 5.5/180.0*np.pi
for i in range(500):
    theta += dtheta
    x = 256    + radius*np.cos(theta)
    y = 256+32 + radius*np.sin(theta)
    r = 10.1-i*0.02;
    radius -= 0.45
    data['a_position'][i] = x,y,0
    data['a_size'][i] = 2*r

for i in range(40):
    r = 4
    thickness = (i+1)/10.0
    x = 20+i*12.5 - 2*r
    y = 16
    data['a_position'][500+i] = x,y,0
    data['a_size'][500+i] = 2*r
    data['a_linewidth'][500+i] = thickness


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self)
        self.size = 1024,1024+2*32
        self.title = "Markers demo [press space to change marker]"

        self.vbo = VertexBuffer(data)
        self.view = np.eye(4,dtype=np.float32)
        self.model = np.eye(4,dtype=np.float32)
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
            Program(markers.vert, markers.frag + markers.ring) ]
                                    
        for program in self.programs:
            program.set_vars(self.vbo,
                             u_antialias = u_antialias,
                             u_size = 1,
                             u_model = self.model,
                             u_view = self.view,
                             u_projection = self.projection)
        self.index = 0
        self.program = self.programs[self.index]

    def on_initialize(self, event):
        gl.glClearColor(1,1,1,1)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(GL.GL_VERTEX_PROGRAM_POINT_SIZE)
        gl.glEnable(GL.GL_POINT_SPRITE)

    def on_key_press(self,event):
        if event.text == ' ':
            self.index = (self.index+1) % (len(self.programs))
            self.program = self.programs[self.index]
            self.program['u_projection'] = self.projection
            self.program['u_size'] = self.u_size
            self.update()

    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)
        self.projection = ortho( 0, width, 0, height, -100, 100 )
        self.u_size = width/512.0
        self.program['u_projection'] = self.projection
        self.program['u_size'] = self.u_size

    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        with self.program as prog:
            prog.draw_arrays(gl.GL_POINTS)

if __name__ == '__main__':
    canvas = Canvas()
    canvas.show()
    app.run()
