#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from vispy import app
from vispy import gloo
from vispy.gloo import gl


# Image
def func(x,y): return (1-x/2+x**5+y**3)*np.exp(-x**2-y**2)
x = np.linspace(-3.0, 3.0, 512).astype(np.float32)
y = np.linspace(-3.0, 3.0, 512).astype(np.float32)
X,Y = np.meshgrid(x, y)
I = func(X,Y)

# Image normalization
vmin,vmax = I.min(), I.max()
I = (I-vmin)/(vmax-vmin)


# Colormaps
colormaps = np.ones((16,512,4)).astype(np.float32)
values = np.linspace(0,1,512)[1:-1]

# Hot colormap
colormaps[0, 0] = 0,0,1,1 # Low values  (< vmin)
colormaps[0,-1] = 0,1,0,1 # High values (> vmax)
colormaps[0,1:-1,0] = np.interp(values, [0.00, 0.33, 0.66, 1.00],
                                        [0.00, 1.00, 1.00, 1.00])
colormaps[0,1:-1,1] = np.interp(values, [0.00, 0.33, 0.66, 1.00],
                                        [0.00, 0.00, 1.00, 1.00])
colormaps[0,1:-1,2] = np.interp(values, [0.00, 0.33, 0.66, 1.00],
                                        [0.00, 0.00, 0.00, 1.00])

# Grey colormap
colormaps[1, 0] = 0,0,1,1 # Low values (< vmin)
colormaps[1,-1] = 0,1,0,1 # High values (> vmax)
colormaps[1,1:-1,0] = np.interp(values, [0.00, 1.00],
                                        [0.00, 1.00])
colormaps[1,1:-1,1] = np.interp(values, [0.00, 1.00],
                                        [0.00, 1.00])
colormaps[1,1:-1,2] = np.interp(values, [0.00, 1.00],
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
uniform vec2 image_shape;

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

class Window(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, show=True, size=(512,512))

        self.image = gloo.Program(img_vertex, img_fragment, 4)
        self.image['position'] = (-1, -1), (-1, +1), (+1, -1), (+1, +1)
        self.image['texcoord'] = (0, 0), (0, +1), (+1, 0), (+1, +1)
        self.image['vmin'] = +0.1
        self.image['vmax'] = +0.9
        self.image['cmap'] = 0 # Colormap index to use

        self.image['colormaps'] = colormaps
        self.image['colormaps'].interpolation = gl.GL_LINEAR
        self.image['colormaps_shape'] = colormaps.shape[1], colormaps.shape[0]

        self.image['image'] = I
        self.image['image'].interpolation = gl.GL_LINEAR
        self.image['image_shape'] = I.shape[1], I.shape[0]

    def on_initialize(self, event):
        gl.glClearColor(0, 0, 0, 1)

    def on_resize(self, event):
        width,height = event.size
        gl.glViewport(0, 0, width, height)

    def on_draw(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.image.draw(gl.GL_TRIANGLE_STRIP)

window = Window()
app.run()
