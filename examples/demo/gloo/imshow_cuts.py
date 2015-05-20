#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Show an image using gloo, with on-mouseover cross-section visualizations.
"""

import numpy as np
from vispy import app
from vispy.gloo import set_viewport, clear, set_state, Program


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


lines_vertex = """
attribute vec2 position;
attribute vec4 color;
varying vec4 v_color;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0 );
    v_color = color;
}
"""

lines_fragment = """
varying vec4 v_color;
void main()
{
    gl_FragColor = v_color;
}
"""


image_vertex = """
attribute vec2 position;
attribute vec2 texcoord;

varying vec2 v_texcoord;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0 );
    v_texcoord = texcoord;
}
"""

image_fragment = """
uniform float vmin;
uniform float vmax;
uniform float cmap;
uniform float n_colormaps;

uniform sampler2D image;
uniform sampler2D colormaps;

varying vec2 v_texcoord;
void main()
{
    float value = texture2D(image, v_texcoord).r;
    float index = (cmap+0.5) / n_colormaps;

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

        self.image = Program(image_vertex, image_fragment, 4)
        self.image['position'] = (-1, -1), (-1, +1), (+1, -1), (+1, +1)
        self.image['texcoord'] = (0, 0), (0, +1), (+1, 0), (+1, +1)
        self.image['vmin'] = +0.0
        self.image['vmax'] = +1.0
        self.image['cmap'] = 0  # Colormap index to use
        self.image['colormaps'] = colormaps
        self.image['n_colormaps'] = colormaps.shape[0]
        self.image['image'] = I.astype('float32')
        self.image['image'].interpolation = 'linear'

        set_viewport(0, 0, *self.physical_size)

        self.lines = Program(lines_vertex, lines_fragment)
        self.lines["position"] = np.zeros((4+4+514+514, 2), np.float32)
        color = np.zeros((4+4+514+514, 4), np.float32)
        color[1:1+2, 3] = 0.25
        color[5:5+2, 3] = 0.25
        color[9:9+512, 3] = 0.5
        color[523:523+512, 3] = 0.5
        self.lines["color"] = color

        set_state(clear_color='white', blend=True,
                  blend_func=('src_alpha', 'one_minus_src_alpha'))

        self.show()

    def on_resize(self, event):
        set_viewport(0, 0, *event.physical_size)

    def on_draw(self, event):
        clear(color=True, depth=True)
        self.image.draw('triangle_strip')
        self.lines.draw('line_strip')

    def on_mouse_move(self, event):
        x, y = event.pos
        w, h = self.size

        # Make sure the mouse isn't outside of the viewport.
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))

        yf = 1 - y/(h/2.)
        xf = x/(w/2.) - 1

        x_norm = (x*512)//w
        y_norm = (y*512)//h

        P = np.zeros((4+4+514+514, 2), np.float32)

        x_baseline = P[:4]
        y_baseline = P[4:8]
        x_profile = P[8:522]
        y_profile = P[522:]

        x_baseline[...] = (-1, yf), (-1, yf), (1, yf), (1, yf)
        y_baseline[...] = (xf, -1), (xf, -1), (xf, 1), (xf, 1)

        x_profile[1:-1, 0] = np.linspace(-1, 1, 512)
        x_profile[1:-1, 1] = yf+0.15*I[y_norm, :]
        x_profile[0] = x_profile[1]
        x_profile[-1] = x_profile[-2]

        y_profile[1:-1, 0] = xf+0.15*I[:, x_norm]
        y_profile[1:-1, 1] = np.linspace(-1, 1, 512)
        y_profile[0] = y_profile[1]
        y_profile[-1] = y_profile[-2]

        self.lines["position"] = P
        self.update()

if __name__ == '__main__':
    canvas = Canvas()
    app.run()
