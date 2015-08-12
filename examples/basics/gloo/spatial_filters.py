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
uniform float     u_interpolation;
varying vec2      v_texcoord;
void main()
{
    // using if-statements here is inefficient
    // used here just for selection of interpolation function
    if (u_interpolation < 0.5) {
        gl_FragColor = Nearest(u_texture, u_shape, v_texcoord);
    }
    else if (u_interpolation < 1.5) {
        gl_FragColor = Bilinear(u_texture, u_shape, v_texcoord);
    }
    else if (u_interpolation < 2.5) {
        gl_FragColor = Hanning(u_texture, u_shape, v_texcoord);
    }
    else if (u_interpolation < 3.5) {
        gl_FragColor = Hamming(u_texture, u_shape, v_texcoord);
    }
    else if (u_interpolation < 4.5) {
        gl_FragColor = Hermite(u_texture, u_shape, v_texcoord);
    }
    else if (u_interpolation < 5.5) {
        gl_FragColor = Kaiser(u_texture, u_shape, v_texcoord);
    }
    else if (u_interpolation < 6.5) {
        gl_FragColor = Quadric(u_texture, u_shape, v_texcoord);
    }
    else if (u_interpolation < 7.5) {
        gl_FragColor = Bicubic(u_texture, u_shape, v_texcoord);
    }
    else if (u_interpolation < 8.5) {
        gl_FragColor = CatRom(u_texture, u_shape, v_texcoord);
    }
    else if (u_interpolation < 9.5) {
        gl_FragColor = Mitchell(u_texture, u_shape, v_texcoord);
    }
    else if (u_interpolation < 10.5) {
        gl_FragColor = Spline16(u_texture, u_shape, v_texcoord);
    }
    else if (u_interpolation < 11.5) {
        gl_FragColor = Spline36(u_texture, u_shape, v_texcoord);
    }
    else if (u_interpolation < 12.5) {
        gl_FragColor = Gaussian(u_texture, u_shape, v_texcoord);
    }
    else if (u_interpolation < 13.5) {
        gl_FragColor = Bessel(u_texture, u_shape, v_texcoord);
    }
    else if (u_interpolation < 14.5) {
        gl_FragColor = Sinc(u_texture, u_shape, v_texcoord);
    }
    else if (u_interpolation < 15.5) {
        gl_FragColor = Lanczos(u_texture, u_shape, v_texcoord);
    }
    else gl_FragColor = Blackman(u_texture, u_shape, v_texcoord);
}

"""


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=((512), (512)))

        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.texture = gloo.Texture2D(I, interpolation='nearest')

        # using internalformat 'r16f' as discussed in issue #1017
        self.kernel = gloo.Texture2D(kernel, interpolation='nearest',
                                     internalformat='r16f')

        self.program['u_texture'] = self.texture
        self.program['u_kernel'] = self.kernel
        self.program['u_shape'] = I.shape[1], I.shape[0]
        self.program['u_interpolation'] = 0

        self.names = tuple(["Nearest"]) + names

        self.title = 'Spatial Filtering using %s Filter' % \
                     self.names[int(self.program['u_interpolation'])]

        self.program.bind(gloo.VertexBuffer(data))

        gloo.set_clear_color('white')

        self.show()

    def on_key_press(self, event):
        if event.key in ['Left', 'Right']:
            if event.key == 'Right':
                step = 1
            else:
                step = -1
            self.program['u_interpolation'] = \
                (self.program['u_interpolation'] + step) % 17
            self.title = 'Spatial Filtering using %s Filter' % \
                         self.names[int(self.program['u_interpolation'])]
            self.update()

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        self.program.draw('triangle_strip')


if __name__ == '__main__':
    c = Canvas()
    app.run()
