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

class Window(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, show=True, size=(512,512))

        self.image = gloo.Program(image_vertex, image_fragment, 4)
        self.image['position'] = (-1, -1), (-1, +1), (+1, -1), (+1, +1)
        self.image['texcoord'] = (0, 0), (0, +1), (+1, 0), (+1, +1)
        self.image['vmin'] = +0.0
        self.image['vmax'] = +1.0
        self.image['cmap'] = 0 # Colormap index to use
        self.image['colormaps'] = colormaps
        self.image['n_colormaps'] = colormaps.shape[0]
        self.image['image'] = I
        self.image['image'].interpolation = gl.GL_LINEAR

        self.lines = gloo.Program(lines_vertex, lines_fragment, 4+4+514+514)
        self.lines["position"] = np.zeros((4+4+514+514,2))
        color = np.zeros((4+4+514+514,4))
        color[1:1+2,3] = 0.25
        color[5:5+2,3] = 0.25
        color[9:9+512,3] = 0.5
        color[523:523+512,3] = 0.5
        self.lines["color"] = color

    def on_initialize(self, event):
        gl.glClearColor(0, 0, 0, 1)

    def on_resize(self, event):
        width,height = event.size
        gl.glViewport(0, 0, width, height)

    def on_draw(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.image.draw(gl.GL_TRIANGLE_STRIP)
        self.lines.draw(gl.GL_LINE_STRIP)

    def on_mouse_move(self, event):
        x,y = event.pos
        yf = 1 - y/256.0
        xf = x/256.0 - 1
        P = np.zeros((4+4+514+514,2))

        x_baseline = P[:4]
        y_baseline = P[4:8]
        x_profile  = P[8:522]
        y_profile  = P[522:]

        x_baseline[...] = (-1,yf), (-1,yf), (1,yf), (1,yf)
        y_baseline[...] = (xf,-1), (xf,-1), (xf,1), (xf,1)

        x_profile[1:-1,0] = np.linspace(-1,1,512)
        x_profile[1:-1,1] = yf+0.15*I[y]
        x_profile[0] = x_profile[1]
        x_profile[-1] = x_profile[-2]

        y_profile[1:-1,0] = xf+0.15*I[:,x]
        y_profile[1:-1,1] = np.linspace(-1,1,512)
        y_profile[0]  = y_profile[1]
        y_profile[-1] = y_profile[-2]


        self.lines["position"] = P
        self.update()

window = Window()
gl.glClearColor(1, 1, 1, 1)
gl.glEnable(gl.GL_BLEND)
gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

app.run()
