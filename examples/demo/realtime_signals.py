#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 2
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Multiple real-time digital signals.
"""

from vispy import gloo
from vispy import app
import numpy as np
import math

nrows = 4
ncols = 5
m = nrows*ncols
n = 1000
amplitudes = .1+.2*np.random.rand(m, 1)
x = np.tile(np.linspace(-1., 1., n), m)
y = amplitudes * np.random.randn(m, n)

position = np.zeros((n*m, 2), dtype=np.float32)
position[:, 0] = x
position[:, 1] = y.ravel()

color = np.repeat(np.random.uniform(size=(m, 3), low=.5, high=.9),
                            n, axis=0)

index = np.c_[np.repeat(np.repeat(np.arange(ncols), nrows), n),
              np.repeat(np.tile(np.arange(nrows), ncols), n)]

VERT_SHADER = """
#version 120
attribute vec2 a_position;
attribute vec2 a_index;
varying vec2 v_index;
uniform vec2 u_scale;
uniform vec2 u_size;

attribute vec3 a_color;
varying vec3 v_color;

void main() {
    float nrows = u_size.x;
    float ncols = u_size.y;
    
    vec2 a = vec2(1./ncols, 1./nrows)*.9;
    vec2 b = vec2(-1+2*(a_index.x+.5)/ncols, -1+2*(a_index.y+.5)/nrows);
    gl_Position = vec4(a*u_scale*a_position+b, 0.0, 1.0);
    v_color = a_color;
    v_index = a_index;
    
    // TODO: allow simultaneous zoom with shader-based clipping.
    // 1. Transform back the coordinates to the original coordinate system.
    // 2. If the position is outside [-1,1]^2, pass a fract v_index to
    //    the fragment shader so as to discard the fragment (clipping).
}
"""

FRAG_SHADER = """
#version 120
varying vec3 v_color;
varying vec2 v_index;
void main() {
    gl_FragColor = vec4(v_color, 1.0);
    if ((fract(v_index.x) > 0.) || (fract(v_index.y) > 0.))
        gl_FragColor.a = 0.;
}
"""


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, close_keys='escape')
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.program['a_position'] = position
        self.program['a_color'] = color
        self.program['a_index'] = index
        self.program['u_scale'] = (1., 1.)
        self.program['u_size'] = (nrows, ncols)
        
        self.timer = app.Timer(1. / 60)
        self.timer.connect(self.on_timer)
        self.timer.start()

    def on_initialize(self, event):
        gloo.set_state(clear_color=(1, 1, 1, 1), blend=True, 
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

    def on_resize(self, event):
        self.width, self.height = event.size
        gloo.set_viewport(0, 0, self.width, self.height)

    def on_timer(self, event):
        y = position[:,1].reshape((m, n))
        y[:,:-10] = y[:,10:]
        y[:,-10:] = amplitudes * np.random.randn(m, 10)
        
        position[:,1] = y.ravel()
        self.program['a_position'].set_data(position)
        self.update()
        
    def on_draw(self, event):
        gloo.clear(color=(0.0, 0.0, 0.0, 1.0))
        self.program.draw('line_strip')
        
if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
