# -*- coding: utf-8 -*-
# vispy: gallery 10
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Show an image using gloo.
"""

import numpy as np
from vispy import app
from vispy.gloo import clear, set_clear_color, set_viewport, Program


# Image
def func(x, y):
    return (1-x/2+x**5+y**3)*np.exp(-x**2-y**2)
x = np.linspace(-3.0, 3.0, 512).astype(np.float32)
y = np.linspace(-3.0, 3.0, 512).astype(np.float32)
X, Y = np.meshgrid(x, y)
I = func(X, Y)

# Image normalization
vmin, vmax = I.min(), I.max()
I = (I-vmin)/(vmax-vmin)


# Colormaps
colormaps = np.ones((16, 512, 4)).astype(np.float32)
values = np.linspace(0, 1, 512)[1:-1]

# Hot colormap
colormaps[0, 0] = 0, 0, 1, 1  # Low values  (< vmin)
colormaps[0, -1] = 0, 1, 0, 1  # High values (> vmax)
colormaps[0, 1:-1, 0] = np.interp(values, [0.00, 0.33, 0.66, 1.00],
                                          [0.00, 1.00, 1.00, 1.00])
colormaps[0, 1:-1, 1] = np.interp(values, [0.00, 0.33, 0.66, 1.00],
                                          [0.00, 0.00, 1.00, 1.00])
colormaps[0, 1:-1, 2] = np.interp(values, [0.00, 0.33, 0.66, 1.00],
                                          [0.00, 0.00, 0.00, 1.00])

# Grey colormap
colormaps[1, 0] = 0, 0, 1, 1  # Low values (< vmin)
colormaps[1, -1] = 0, 1, 0, 1  # High values (> vmax)
colormaps[1, 1:-1, 0] = np.interp(values, [0.00, 1.00],
                                          [0.00, 1.00])
colormaps[1, 1:-1, 1] = np.interp(values, [0.00, 1.00],
                                          [0.00, 1.00])
colormaps[1, 1:-1, 2] = np.interp(values, [0.00, 1.00],
                                          [0.00, 1.00])
# Jet colormap
# ...


img_vertex = """
attribute vec2 position;
attribute vec2 texcoord;

varying vec2 v_texcoord;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0 );
    v_texcoord = texcoord;
}
"""

img_fragment = """
uniform float vmin;
uniform float vmax;
uniform float cmap;

uniform sampler2D image;
uniform sampler2D colormaps;
uniform vec2 colormaps_shape;

varying vec2 v_texcoord;
void main()
{
    float value = texture2D(image, v_texcoord).r;
    float index = (cmap+0.5) / colormaps_shape.y;

    if( value < vmin ) {
        gl_FragColor = texture2D(colormaps, vec2(0.0,index));
    } else if( value > vmax ) {
        gl_FragColor = texture2D(colormaps, vec2(1.0,index));
    } else {
        value = (value-vmin)/(vmax-vmin);
        value = 1.0/512.0 + 510.0/512.0*value;
        gl_FragColor = texture2D(colormaps, vec2(value,index));
    }
}
"""


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(512, 512),
                            keys='interactive')
        self.image = Program(img_vertex, img_fragment, 4)
        self.image['position'] = (-1, -1), (-1, +1), (+1, -1), (+1, +1)
        self.image['texcoord'] = (0, 0), (0, +1), (+1, 0), (+1, +1)
        self.image['vmin'] = +0.1
        self.image['vmax'] = +0.9
        self.image['cmap'] = 0  # Colormap index to use

        self.image['colormaps'] = colormaps
        self.image['colormaps'].interpolation = 'linear'
        self.image['colormaps_shape'] = colormaps.shape[1], colormaps.shape[0]

        self.image['image'] = I.astype('float32')
        self.image['image'].interpolation = 'linear'

        set_clear_color('black')

        self.show()

    def on_resize(self, event):
        width, height = event.physical_size
        set_viewport(0, 0, *event.physical_size)

    def on_draw(self, event):
        clear(color=True, depth=True)
        self.image.draw('triangle_strip')

if __name__ == '__main__':
    canvas = Canvas()
    app.run()
