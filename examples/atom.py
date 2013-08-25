#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# VisPy - Copyright (c) 2013, Vispy Development Team
# All rights reserved.
# -----------------------------------------------------------------------------
"""
Particles orbiting around a central point (with traces)
"""

import numpy as np
from OpenGL import GL
from vispy import oogl
from vispy import app
from vispy import gl
from transforms import perspective, translate, rotate


n = 200
p = 50
T = np.random.uniform(0,2*np.pi,n)
a_position = np.zeros((n,2),dtype=np.float32)
a_position[:,0] = np.cos(T)
a_position[:,1] = np.sin(T)
a_rot = np.random.uniform(0,2*np.pi,(n,2)).astype(np.float32)
a_color = np.ones((n,4),dtype=np.float32) * (1,1,1,1)
u_size = 3
u_linewidth = 1.0
u_antialias = 1.0

a_position = np.repeat(a_position, p, axis=0)
a_color    = np.repeat(a_color,    p, axis=0)
a_rot      = np.repeat(a_rot,      p, axis=0)


VERT_SHADER = """
#version 120

// Uniforms
// ------------------------------------
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform float u_linewidth;
uniform float u_antialias;
uniform float u_size;

// Attributes
// ------------------------------------
attribute vec2  a_position;
attribute vec2  a_rot;
attribute vec4  a_color;
attribute mat4  a_model;

// Varyings
// ------------------------------------
varying vec4 v_color;
varying float v_size;
varying float v_linewidth;
varying float v_antialias;

mat4 rotation(vec3 axis, float angle)
{
    axis = normalize(axis);
    float s = sin(angle);
    float c = cos(angle);
    float oc = 1.0 - c;
    return mat4(oc * axis.x * axis.x + c,
                oc * axis.x * axis.y - axis.z * s,
                oc * axis.z * axis.x + axis.y * s,
                0.0,
                oc * axis.x * axis.y + axis.z * s,
                oc * axis.y * axis.y + c,
                oc * axis.y * axis.z - axis.x * s,
                0.0,
                oc * axis.z * axis.x - axis.y * s,
                oc * axis.y * axis.z + axis.x * s,
                oc * axis.z * axis.z + c,
                0.0,
                0.0, 0.0, 0.0, 1.0);
}

void main (void) {
    v_size = u_size;
    v_linewidth = u_linewidth;
    v_antialias = u_antialias;
    v_color = a_color;

    mat4 X = rotation(vec3(1,0,0), a_rot.x);
    mat4 Y = rotation(vec3(0,1,0), a_rot.y);
    gl_Position = u_projection * u_view * u_model * Y * X * vec4(a_position, 0.0, 1.0);
    gl_PointSize = v_size + 2*(v_linewidth + 1.5*v_antialias);
}
"""

FRAG_SHADER = """
#version 120

// Varyings
// ------------------------------------
varying vec4 v_color;
varying float v_size;
varying float v_linewidth;
varying float v_antialias;


// Main
// ------------------------------------
void main()
{    
    float d = 2*(length(gl_PointCoord.xy - vec2(0.5,0.5))); // (2*sqrt(2.0)));
    gl_FragColor = vec4(v_color.rgb, v_color.a*(1-d));
}
"""



# -----------------------------------------------------------------------------
class Canvas(app.Canvas):

    # ---------------------------------
    def __init__(self):
        app.Canvas.__init__(self)
        self.geometry = (0,0,800,800)
        self.program = oogl.ShaderProgram( oogl.VertexShader(VERT_SHADER), 
                                           oogl.FragmentShader(FRAG_SHADER) )
        # Set uniform and attribute
        self.program.attributes['a_color'] = a_color
        self.program.attributes['a_position'] = a_position
        self.program.attributes['a_rot']      = a_rot
        self.program.uniforms['u_linewidth']  = u_linewidth
        self.program.uniforms['u_antialias']  = u_antialias
        self.program.uniforms['u_size']       = u_size

        self.view       = np.eye(4,dtype=np.float32)
        self.model      = np.eye(4,dtype=np.float32)
        self.projection = np.eye(4,dtype=np.float32)

        self.translate = 3
        translate(self.view, 0,0, -self.translate)
        self.program.uniforms['u_model'] = self.model
        self.program.uniforms['u_view'] = self.view

        self.theta = 0
        self.phi = 0
        self.index = 0

        self.timer = app.Timer(1.0/400)
        self.timer.connect(self.on_timer)
        self.timer.start()

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
        self.theta += .017
        self.phi += .013
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
        global u_size

        self.translate +=event.delta[1]
        self.translate = max(2,self.translate)
        self.view       = np.eye(4,dtype=np.float32)
        translate(self.view, 0,0, -self.translate)
        self.program.uniforms['u_view'] = self.view
        self.update()


    # ---------------------------------
    def on_paint(self, event):
        global T,p,n

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        self.index = (self.index+1)%p
        T += np.pi/200
        a_position[self.index::p,0] = np.cos(T)
        a_position[self.index::p,1] = np.sin(T)
        a_color[:,3] -= 1.0/p
        a_color[self.index::p,3] = 1
        with self.program as prog:
            self.program.attributes['a_position'] = a_position
            self.program.attributes['a_color'] = a_color
            prog.draw_arrays(gl.GL_POINTS)


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
