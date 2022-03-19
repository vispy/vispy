#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 3
"""
Use FrameBuffers
================

Minimal example demonstrating the use of frame buffer objects (FBO).
This example blurs the output image.

"""


from vispy import gloo
from vispy import app
import numpy as np

# Create vertices
vPosition = np.array([[-0.8, -0.8, 0.0], [+0.7, -0.7, 0.0],
                      [-0.7, +0.7, 0.0], [+0.8, +0.8, 0.0, ]], np.float32)
vPosition_full = np.array([[-1.0, -1.0, 0.0], [+1.0, -1.0, 0.0],
                           [-1.0, +1.0, 0.0], [+1.0, +1.0, 0.0, ]], np.float32)
vTexcoord = np.array([[0.0, 0.0], [0.0, 1.0],
                      [1.0, 0.0], [1.0, 1.0]], np.float32)

# For initial quad
VERT_SHADER1 = """
attribute vec3 a_position;
void main (void) {
    gl_Position = vec4(a_position, 1.0);
}
"""

FRAG_SHADER1 = """
uniform vec4 u_color;
void main()
{
    gl_FragColor = u_color;
}
"""

# To render the result of the FBO
VERT_SHADER2 = """
attribute vec3 a_position;
attribute vec2 a_texcoord;
varying vec2 v_texcoord;
void main (void) {
    // Pass tex coords
    v_texcoord = a_texcoord;
    // Calculate position
    gl_Position = vec4(a_position.x, a_position.y, a_position.z, 1.0);
}
"""

FRAG_SHADER2 = """
uniform sampler2D u_texture1;
varying vec2 v_texcoord;
const float c_zero = 0.0;
const int c_sze = 5;
void main()
{
    float scalefactor = 1.0 / float(c_sze * c_sze * 4 + 1);
    gl_FragColor = vec4(c_zero, c_zero, c_zero, 1.0);
    for (int y=-c_sze; y<=c_sze; y++) {
        for (int x=-c_sze; x<=c_sze; x++) {
            vec2 step = vec2(x,y) * 0.01;
            vec3 color = texture2D(u_texture1, v_texcoord.st+step).rgb;
            gl_FragColor.rgb += color * scalefactor;
        }
    }
}
"""


SIZE = 50


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=(560, 420))

        # Create texture to render to
        shape = self.physical_size[1], self.physical_size[0]
        self._rendertex = gloo.Texture2D((shape + (3,)))

        # Create FBO, attach the color buffer and depth buffer
        self._fbo = gloo.FrameBuffer(self._rendertex, gloo.RenderBuffer(shape))

        # Create program to render a shape
        self._program1 = gloo.Program(VERT_SHADER1, FRAG_SHADER1)
        self._program1['u_color'] = 0.9, 1.0, 0.4, 1
        self._program1['a_position'] = gloo.VertexBuffer(vPosition)

        # Create program to render FBO result
        self._program2 = gloo.Program(VERT_SHADER2, FRAG_SHADER2)
        self._program2['a_position'] = gloo.VertexBuffer(vPosition)
        self._program2['a_texcoord'] = gloo.VertexBuffer(vTexcoord)
        self._program2['u_texture1'] = self._rendertex

        self.show()

    def on_resize(self, event):
        width, height = event.physical_size
        gloo.set_viewport(0, 0, width, height)

    def on_draw(self, event):
        # Draw the same scene as as in hello_quad.py, but draw it to the FBO
        with self._fbo:
            gloo.set_clear_color((0.0, 0.0, 0.5, 1))
            gloo.clear(color=True, depth=True)
            gloo.set_viewport(0, 0, *self.physical_size)
            self._program1.draw('triangle_strip')

        # Now draw result to a full-screen quad
        # Init
        gloo.set_clear_color('white')
        gloo.clear(color=True, depth=True)
        self._program2.draw('triangle_strip')


if __name__ == '__main__':
    canvas = Canvas()
    app.run()
