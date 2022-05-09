#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 2
"""
Spatial Filtering
=================

Example demonstrating spatial filtering using spatial-filters fragment shader.

Left and Right Arrow Keys toggle through available filters.

"""

import numpy as np

from vispy.io import load_spatial_filters
from vispy import gloo
from vispy import app
from vispy.util.logs import set_log_level
# turn off INFO messages, see PR #1363
# Some shader compilers will optimize out the 'u_shape' and 'u_kernel'
# uniforms for the Nearest filter since they are unused, resulting in
# an INFO message about them not being active
set_log_level('warning')

# create 5x5 matrix with border pixels 0, center pixels 1
# and other pixels 0.5
img_array = np.zeros(25).reshape((5, 5)).astype(np.float32)
img_array[1:4, 1::2] = 0.5
img_array[1::2, 2] = 0.5
img_array[2, 2] = 1.0

# loading interpolation kernel
kernel, names = load_spatial_filters()
names = [name + '2D' for name in names]

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

        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER % 'Nearest2D')
        self.texture = gloo.Texture2D(img_array, interpolation='nearest')

        # using packed data as discussed in pr #1069
        self.kernel = gloo.Texture2D(kernel, interpolation='nearest')
        self.program['u_texture'] = self.texture
        self.program['u_shape'] = img_array.shape[1], img_array.shape[0]
        self.program['u_kernel'] = self.kernel

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

            self.title = 'Spatial Filtering using %s Filter' % \
                         self.names[self.filter]
            self.update()

    def on_resize(self, event):
        self.context.set_viewport(0, 0, *event.physical_size)

    def on_draw(self, event):
        self.context.clear(color=True, depth=True)
        self.program.draw('triangle_strip')


if __name__ == '__main__':
    canvas = Canvas()
    app.run()
