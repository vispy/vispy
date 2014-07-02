#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 2
"""
Example demonstrating a 3D Texture

"""

import numpy as np

from vispy.util.transforms import ortho
from vispy import gloo
from vispy import app
from vispy.gloo import gl

import OpenGL.GL as glext

from vispy.util import logger,use_log_level

use_log_level('debug')


# Image to be displayed
S=64
W, H, D = S,S,S
#I = np.random.uniform(0, 1, (W, H, D)).astype(np.float32)

#gradient
I=np.linspace(0.0,1.0,S).astype(np.float32)
I=np.tile(I,(S,S,1))

# A simple texture quad
data = np.zeros(4, dtype=[('a_position', np.float32, 2),
                          ('a_texcoord', np.float32, 2)])
data['a_position'] = np.array([[0, 0], [W, 0], [0, H], [W, H]])
data['a_texcoord'] = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])


VERT_SHADER = """
// Uniforms
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform float u_antialias;

// Attributes
attribute vec2 a_position;
attribute vec2 a_texcoord;

// Varyings
varying vec2 v_texcoord;

// Main
void main (void)
{
    v_texcoord = a_texcoord;
    gl_Position = u_projection * u_view * u_model * vec4(a_position,0.0,1.0);
}
"""

FRAG_SHADER = """
uniform sampler3D u_texture;
uniform float i;
varying vec2 v_texcoord;
void main()
{
// step through gradient with i
    gl_FragColor = texture3D(u_texture, vec3(i,v_texcoord));
    gl_FragColor.a = 1.0;
}

"""


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, close_keys='escape')
        self.size = W * 5, H * 5

        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.texture = gloo.Texture3D(I)
        self.texture.interpolation = gl.GL_LINEAR

        self.program['u_texture'] = self.texture
        self.program['i']=0.0
        self.program.bind(gloo.VertexBuffer(data))

        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        self.projection = ortho(0, W, 0, H, -1, 1)
        self.program['u_projection'] = self.projection
        
        self.i=0;

    def on_initialize(self, event):
        gl.glClearColor(1, 1, 1, 1)

    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)
        self.projection = ortho(0, width, 0, height, -100, 100)
        self.program['u_projection'] = self.projection

        # Compute thje new size of the quad
        r = width / float(height)
        R = W / float(H)
        if r < R:
            w, h = width, width / R
            x, y = 0, int((height - h) / 2)
        else:
            w, h = height * R, height
            x, y = int((width - w) / 2), 0
        data['a_position'] = np.array(
            [[x, y], [x + w, y], [x, y + h], [x + w, y + h]])
        self.program.bind(gloo.VertexBuffer(data))

    def on_draw(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        #I[...] = np.random.uniform(0, 1, (W, H, D)).astype(np.float32)
        #self.texture.set_data(I)
        self.program['i']=self.i
        self.program.draw(gl.GL_TRIANGLE_STRIP)
        self.update()
        
        self.i=(self.i+0.01)%1.0
        #gl.check_error()


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
