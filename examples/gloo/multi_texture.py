#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 2
"""
Use multiple textures
=====================

We create two textures. One that shows a red, green and blue band in
the horizontal direction and one that does the same in the vertical
direction. In the fragment shader the colors from both textures are
added.

"""

import numpy as np

from vispy import gloo
from vispy import app


# Images to be displayed
W, H = 30, 30
im1 = np.zeros((W, H, 3), np.float32)
im2 = np.zeros((W, H, 3), np.float32)
im1[:10, :, 0] = 1.0
im1[10:20, :, 1] = 1.0
im1[20:, :, 2] = 1.0
im2[:, :10, 0] = 1.0
im2[:, 10:20, 1] = 1.0
im1[:, 20:, 2] = 1.0

# A simple texture quad
data = np.zeros(4, dtype=[('a_position', np.float32, 2),
                          ('a_texcoord', np.float32, 2)])
data['a_position'] = np.array([[-1, -1], [+1, -1], [-1, +1], [+1, +1]])
data['a_texcoord'] = np.array([[1, 0], [1, 1.2], [0, 0], [0, 1.2]])


VERT_SHADER = """
attribute vec2 a_position;
attribute vec2 a_texcoord;
varying vec2 v_texcoord;

void main (void)
{
    v_texcoord = a_texcoord;
    gl_Position = vec4(a_position, 0.0, 1.0);
}
"""

FRAG_SHADER = """
uniform sampler2D u_tex1;
uniform sampler2D u_tex2;
varying vec2 v_texcoord;

void main()
{
    vec3 clr1 = texture2D(u_tex1, v_texcoord).rgb;
    vec3 clr2 = texture2D(u_tex2, v_texcoord).rgb;
    gl_FragColor.rgb = clr1 + clr2;
    gl_FragColor.a = 1.0;
}
"""


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, size=(500, 500), keys='interactive')

        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.program['u_tex1'] = gloo.Texture2D(im1, interpolation='linear')
        self.program['u_tex2'] = gloo.Texture2D(im2, interpolation='linear')
        self.program.bind(gloo.VertexBuffer(data))

        gloo.set_clear_color('white')

        self.show()

    def on_resize(self, event):
        width, height = event.physical_size
        gloo.set_viewport(0, 0, width, height)

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        self.program.draw('triangle_strip')


if __name__ == '__main__':
    canvas = Canvas()
    app.run()
