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
image = func(X,Y)


# Colormaps
colormaps = np.ones((16,512,4)).astype(np.float32)

# Hot colormap
colormaps[0,:,0] = np.interp(np.linspace(0,1,512),
                             [0.00, 0.33, 0.66, 1.00],
                             [0.00, 1.00, 1.00, 1.00])
colormaps[0,:,1] = np.interp(np.linspace(0,1,512),
                             [0.00, 0.33, 0.66, 1.00],
                             [0.00, 0.00, 1.00, 1.00])
colormaps[0,:,2] = np.interp(np.linspace(0,1,512),
                             [0.00, 0.33, 0.66, 1.00],
                             [0.00, 0.00, 0.00, 1.00])

# Grey colormap
colormaps[1,:,0] = np.interp(np.linspace(0,1,512),
                             [0.00, 1.00],
                             [0.00, 1.00])
colormaps[1,:,1] = np.interp(np.linspace(0,1,512),
                             [0.00, 1.00],
                             [0.00, 1.00])
colormaps[1,:,2] = np.interp(np.linspace(0,1,512),
                             [0.00, 1.00],
                             [0.00, 1.00])
# Jet colormap
# ...


vertex = """
attribute vec2 position;
attribute vec2 texcoord;

varying vec2 v_texcoord;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0 );
    v_texcoord = texcoord;
}
"""

fragment = """

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
    value = (value-vmin)/(vmax-vmin);

    float index = (cmap+.5) / n_colormaps;
    vec4 color = texture2D(colormaps, vec2(value,index));
    gl_FragColor = color;
}
"""

class Window(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, show=True, size=(512,512))
        self.program = gloo.Program(vertex, fragment, 4)
        self.program['position'] = (-1, -1), (-1, +1), (+1, -1), (+1, +1)
        self.program['texcoord'] = (0, 0), (0, +1), (+1, 0), (+1, +1)
        self.program['vmin'] = +0.0
        self.program['vmax'] = +1.0
        self.program['cmap'] = 1 # Colormap index to use

        self.program['colormaps'] = colormaps
        self.program['n_colormaps'] = colormaps.shape[0]
        self.program['image'] = image
        self.program['image'].interpolation = gl.GL_LINEAR
        self.translate = np.array([0,0], dtype=np.float32)

    def on_initialize(self, event):
        gl.glClearColor(0, 0, 0, 1)

    def on_resize(self, event):
        width,height = event.size
        gl.glViewport(0, 0, width, height)

    def on_draw(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.program.draw(gl.GL_TRIANGLE_STRIP)

window = Window()
app.run()
