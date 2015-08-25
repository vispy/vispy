#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example demonstrating spatial filtering using spatial-filters fragment shader.
Left and Right Arrow Keys toggle through available filters.
"""

import numpy as np

from vispy.io import load_spatial_filters
from vispy import gloo
from vispy import app

# create 5x5 matrix with border pixels 0, center pixels 1
# and other pixels 0.5
I = np.zeros(25).reshape((5, 5)).astype(np.float32)
I[1:4, 1::2] = 0.5
I[1::2, 2] = 0.5
I[2, 2] = 1.0

# loading interpolation kernel
kernel, names = load_spatial_filters()

# A simple texture quad
data = np.zeros(4, dtype=[('a_position', np.float32, 2),
                          ('a_texcoord', np.float32, 2)])
data['a_position'] = np.array([[-1, -1], [+1, -1], [-1, +1], [+1, +1]])
data['a_texcoord'] = np.array([[1, 0], [1, 1], [0, 0], [0, 1]])


VERT_SHADER = """
// Attributes
attribute vec2 a_position;
attribute vec2 a_texcoord;

// Varyings
varying vec2 v_texcoord;

// Main
void main (void)
{
    v_texcoord = a_texcoord;
    gl_Position = vec4(a_position,0.0,1.0);
}
"""

FRAG_SHADER = """
#include "misc/spatial-filters.frag"
uniform sampler2D u_texture;
uniform vec2      u_shape;
varying vec2      v_texcoord;
void main()
{
    gl_FragColor = %s(u_texture, u_shape, v_texcoord);
}

"""


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=((512), (512)))

        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER % 'Nearest')
        self.texture = gloo.Texture2D(I, interpolation='nearest')

        # using packed data as discussed in pr #1069
        self.kernel = gloo.Texture2D(kernel, interpolation='nearest')
        self.program['u_texture'] = self.texture

        self.names = names
        self.filter = 16
        self.title = 'Spatial Filtering using %s Filter' % \
                     self.names[self.filter]

        self.program.bind(gloo.VertexBuffer(data))

        self.context.set_clear_color('white')
        self.context.set_viewport(0, 0, 512, 512)
        self.show()

    def on_key_press(self, event):
        if event.key in ['Left', 'Right']:
            if event.key == 'Right':
                step = 1
            else:
                step = -1
            self.filter = (self.filter + step) % 17
            self.program.set_shaders(VERT_SHADER,
                                     FRAG_SHADER % self.names[self.filter])

            if self.names[self.filter] != 'Nearest':
                self.program['u_kernel'] = self.kernel
                self.program['u_shape'] = I.shape[1], I.shape[0]
            self.title = 'Spatial Filtering using %s Filter' % \
                         self.names[self.filter]
            self.update()

    def on_resize(self, event):
        self.context.set_viewport(0, 0, *event.physical_size)

    def on_draw(self, event):
        self.context.clear(color=True, depth=True)
        self.program.draw('triangle_strip')


if __name__ == '__main__':
    c = Canvas()
    app.run()
