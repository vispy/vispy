# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code of this example should be considered public domain.

"""
Just a very fake galaxy.
Astronomers and cosmologists will kill me !
"""

import os
from vispy import oogl
from vispy import app
from vispy import gl
from OpenGL import GL
import numpy as np
from transforms import perspective, translate, rotate

#app.use('glut')
app.use('qt')

def make_arm(n,angle):
    R = np.linspace(10,500,n)          + 50*np.random.normal(0,2,n) * np.linspace(1,.1,n)
    T = angle+np.linspace(0,2*np.pi,n) + np.pi/6*np.random.normal(0,.5,n)
    S = 5+3*np.abs(np.random.normal(0,1,n))
    S *= np.linspace(.5,1.,n)
    X = R*np.cos(T)
    Y = R*np.sin(T)
    D = np.sqrt(X*X+Y*Y)
    Z = 8*np.random.normal(0, 2-D/512., n)
    D = np.maximum(0,D+25*np.random.normal(0,1,n))

    return X/256,Y/256,Z/256,S/2,D

p = 250000
n = 3*p
a_position = np.zeros((n,3),np.float32)
a_size     = np.random.uniform(.5,1,(n,1)).astype(np.float32)
a_dist     = np.ones((n,1))

for i in range(3):
    X,Y,Z,S,D = make_arm(p, i * 2*np.pi/3)
    a_dist[(i+0)*p:(i+1)*p,0] = D 
    a_position[(i+0)*p:(i+1)*p,0] = X
    a_position[(i+0)*p:(i+1)*p,1] = Y
    a_position[(i+0)*p:(i+1)*p,2] = Z
    a_size[(i+0)*p:(i+1)*p,0] = S


# Define marker array
spectrum = 'spectrum.png'
THISDIR = os.path.dirname(os.path.abspath(__file__))
spectrum_filename = os.path.join(THISDIR, 'data', spectrum)

VERT_SHADER = """
#version 120

// Uniforms
// ------------------------------------
uniform mat4      u_model;
uniform mat4      u_view;
uniform mat4      u_projection;
uniform sampler2D u_texture;


// Attributes
// ------------------------------------
attribute vec3  a_position;
attribute float a_size;
attribute float a_dist;

// Varyings
// ------------------------------------
varying float v_size;
varying float v_dist;

void main (void) {
    v_size  = a_size;
    v_dist  = a_dist/512.0;
    v_dist  = .15+.4*v_dist;
    gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
    gl_PointSize = v_size;
}
"""

FRAG_SHADER = """
#version 120

// Uniforms
// ------------------------------------
uniform sampler2D u_texture;

// Varyings
// ------------------------------------
varying float v_size;
varying float v_dist;

// Main
// ------------------------------------
void main()
{    
    float a = 2*(length(gl_PointCoord.xy - vec2(0.5,0.5)) / sqrt(2));
    vec3 color = texture2D(u_texture, vec2(v_dist,.5)).rgb;
    gl_FragColor = vec4(color, (1-a)/v_size);
}
"""



class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self)
        self.geometry = (0,0,1024,1024)
        self.title = "A very fake galaxy"

        self.program = oogl.ShaderProgram( oogl.VertexShader(VERT_SHADER), 
                                           oogl.FragmentShader(FRAG_SHADER) )
        # Set uniform and attribute
        self.program.attributes['a_position'] = a_position
        self.program.attributes['a_dist']     = a_dist
        self.program.attributes['a_size']     = a_size

        from PIL import Image
        im = Image.open(spectrum_filename)
        self.program.uniforms['u_texture'] = oogl.Texture2D(np.asarray(im))

        self.view       = np.eye(4,dtype=np.float32)
        self.model      = np.eye(4,dtype=np.float32)
        self.projection = np.eye(4,dtype=np.float32)

        self.translate = 5
        translate(self.view, 0,0, -self.translate)
        self.program.uniforms['u_model'] = self.model
        self.program.uniforms['u_view'] = self.view

        self.theta = 0
        self.phi = 0

        self.timer = app.Timer(1.0/60)
        self.timer.connect(self.on_timer)
#        self.timer.start()

    # ---------------------------------
    def on_initialize(self, event):
        gl.glClearColor(0,0,0,1)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(GL.GL_VERTEX_PROGRAM_POINT_SIZE)
        gl.glEnable(GL.GL_POINT_SPRITE)

    # ---------------------------------
    def on_key_press(self,event):
        if event.text == ' ':
            if self.timer.running:
                self.timer.stop()
            else:
                self.timer.start()

    # ---------------------------------
    def on_timer(self,event):
        self.theta += .11
        self.phi += .13
        self.model = np.eye(4, dtype=np.float32)
        rotate(self.model, self.theta, 0,0,1)
        rotate(self.model, self.phi,   0,1,0)
        self.program.uniforms['u_model'] = self.model
        self.update()


    # ---------------------------------
    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)
        self.projection = perspective( 45.0, width/float(height), 1.0, 1000.0 )
        self.program.uniforms['u_projection'] = self.projection


    # ---------------------------------
    def on_mouse_wheel(self, event):
        self.translate +=event.delta[1]
        self.translate = max(2,self.translate)
        self.view       = np.eye(4,dtype=np.float32)
        translate(self.view, 0,0, -self.translate)
        self.program.uniforms['u_view'] = self.view
        self.program.attributes['a_size'] = a_size*5/self.translate
        self.update()

    # ---------------------------------
    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        with self.program as prog:
            prog.draw_arrays(gl.GL_POINTS)
        self.swap_buffers()

if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
