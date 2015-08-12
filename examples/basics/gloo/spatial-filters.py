#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 2
"""
Example demonstrating spatial filtering using spatial-filters fragment shader.
Left and Right Arrow Keys toggle through available filters.
"""

import os
import numpy as np

from vispy.util.transforms import ortho
from vispy.io import _data_dir
from vispy import gloo
from vispy import app


# Image to be displayed
W, H = 100, 100
I = np.random.uniform(0,1,(5,5,3)).astype(np.float32)

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
#include "misc/spatial-filters.frag"
uniform sampler2D u_texture;
uniform vec2      u_shape;
uniform float     u_interpolation;
varying vec2 v_texcoord;
void main()
{
    //gl_FragColor = texture2D(u_texture, v_texcoord);
    //gl_FragColor.a = 1.0;
    
    if (u_interpolation < 0.5)       gl_FragColor = Nearest(u_texture, u_shape, v_texcoord);
    else if (u_interpolation < 1.5)  gl_FragColor = Bilinear(u_texture, u_shape, v_texcoord);
    else if (u_interpolation < 2.5)  gl_FragColor = Hanning(u_texture, u_shape, v_texcoord);
    else if (u_interpolation < 3.5)  gl_FragColor = Hamming(u_texture, u_shape, v_texcoord);
    else if (u_interpolation < 4.5)  gl_FragColor = Hermite(u_texture, u_shape, v_texcoord);
    else if (u_interpolation < 5.5)  gl_FragColor = Kaiser(u_texture, u_shape, v_texcoord);
    else if (u_interpolation < 6.5)  gl_FragColor = Quadric(u_texture, u_shape, v_texcoord);
    else if (u_interpolation < 7.5)  gl_FragColor = Bicubic(u_texture, u_shape, v_texcoord);
    else if (u_interpolation < 8.5)  gl_FragColor = CatRom(u_texture, u_shape, v_texcoord);
    else if (u_interpolation < 9.5)  gl_FragColor = Mitchell(u_texture, u_shape, v_texcoord);
    else if (u_interpolation < 10.5) gl_FragColor = Spline16(u_texture, u_shape, v_texcoord);
    else if (u_interpolation < 11.5) gl_FragColor = Spline36(u_texture, u_shape, v_texcoord);
    else if (u_interpolation < 12.5) gl_FragColor = Gaussian(u_texture, u_shape, v_texcoord);
    else if (u_interpolation < 13.5) gl_FragColor = Bessel(u_texture, u_shape, v_texcoord);
    else if (u_interpolation < 14.5) gl_FragColor = Sinc(u_texture, u_shape, v_texcoord);
    else if (u_interpolation < 15.5) gl_FragColor = Lanczos(u_texture, u_shape, v_texcoord);
    else                             gl_FragColor = Blackman(u_texture, u_shape, v_texcoord);
}

"""


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=((W*5), (H*5)))

        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.texture = gloo.Texture2D(I, interpolation='nearest')

        self.kernel = gloo.Texture2D(np.load(os.path.join(_data_dir, 'spatial-filters.npy')),
                                     interpolation='nearest')

        self.program['u_texture'] = self.texture
        self.program['u_kernel'] = self.kernel
        self.program['u_shape'] = I.shape[1], I.shape[0]
        self.program['u_interpolation'] = 0

        self.names = [
            "Nearest", "Bilinear", "Hanning", "Hamming",
            "Hermite", "Kaiser", "Quadric", "Bicubic",
            "CatRom", "Mitchell", "Spline16", "Spline36",
            "Gaussian", "Bessel", "Sinc", "Lanczos", "Blackman"]

        self.title = 'Spatial Filtering using %s Filter' % \
                     self.names[int(self.program['u_interpolation'])]

        self.program.bind(gloo.VertexBuffer(data))

        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        self.projection = ortho(0, W, 0, H, -1, 1)
        self.program['u_projection'] = self.projection

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

    def on_resize(self, event):
        width, height = event.physical_size
        gloo.set_viewport(0, 0, width, height)
        self.projection = ortho(0, width, 0, height, -100, 100)
        self.program['u_projection'] = self.projection

        # Compute the new size of the quad
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
        gloo.clear(color=True, depth=True)
        self.program.draw('triangle_strip')


if __name__ == '__main__':
    c = Canvas()
    app.run()
