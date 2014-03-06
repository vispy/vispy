# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author:   Almar Klein & Nicolas P .Rougier
# Date:     04/03/2014
# Topic:    Fireworks !
# Keywords: oarticles, gl, sprites
# -----------------------------------------------------------------------------
"""
Example demonstrating simulation of fireworks using point sprites.
(adapted from the "OpenGL ES 2.0 Programming Guide")

This example demonstrates a series of explosions that last one second. The
visualization during the explosion is highly optimized using a Vertex Buffer
Object (VBO). After each explosion, vertex data for the next explosion are
calculated, such that each explostion is unique.
"""
import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut


vertex_code = """
#version 120

uniform float time;
uniform vec3 center;
attribute float lifetime;
attribute vec3 start;
attribute vec3 end;
varying float v_lifetime;
void main () {
    if (time < lifetime) {
        gl_Position.xyz = start + (time * end) + center;
        gl_Position.w = 1.0;
        gl_Position.y -= 1.5 * time * time;
    } else {
        gl_Position = vec4(-1000, -1000, 0, 0);
    }
    v_lifetime = clamp(1.0 - (time / lifetime), 0.0, 1.0);
    gl_PointSize = (v_lifetime * v_lifetime) * 40.0;
}
"""

fragment_code = """
#version 120

uniform vec4 color;
varying float v_lifetime;
void main()
{
    float d = 1 - length(gl_PointCoord - vec2(.5,.5)) / (sqrt(2)/2);
    gl_FragColor = d*color;
    gl_FragColor.a = d;
    gl_FragColor.a *= v_lifetime;
}
"""


def display():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glDrawArrays(gl.GL_POINTS, 0, len(data))
    glut.glutSwapBuffers()


def reshape(width, height):
    gl.glViewport(0, 0, width, height)


def keyboard(key, x, y):
    if key == '\033':
        sys.exit()


def new_explosion():
    n = len(data)

    color = np.random.uniform(0.1, 0.9, 4).astype(np.float32)
    color[3] = 1.0 / n ** 0.08
    loc = gl.glGetUniformLocation(program, "color")
    gl.glUniform4f(loc, *color)

    center = np.random.uniform(-0.5, 0.5, 3)
    loc = gl.glGetUniformLocation(program, "center")
    gl.glUniform3f(loc, *center)

    data['lifetime'] = np.random.normal(2.0, 0.5, (n,))
    data['start'] = np.random.normal(0.0, 0.2, (n, 3))
    data['end'] = np.random.normal(0.0, 1.2, (n, 3))
    gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_DYNAMIC_DRAW)


def timer(fps):
    global elapsed_time

    elapsed_time += 1.0 / fps
    if elapsed_time > 1.5:
        new_explosion()
        elapsed_time = 0.0

    loc = gl.glGetUniformLocation(program, "time")
    gl.glUniform1f(loc, elapsed_time)

    glut.glutTimerFunc(1000 / fps, timer, fps)
    glut.glutPostRedisplay()


# GLUT init
# --------------------------------------
glut.glutInit()
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
glut.glutCreateWindow("GL Fireworks")
glut.glutReshapeWindow(800, 600)
glut.glutReshapeFunc(reshape)
glut.glutDisplayFunc(display)
glut.glutKeyboardFunc(keyboard)
glut.glutTimerFunc(1000 / 60, timer, 60)

# Build & activate program
# --------------------------------------
program = gl.glCreateProgram()
vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
gl.glShaderSource(vertex, vertex_code)
gl.glShaderSource(fragment, fragment_code)
gl.glCompileShader(vertex)
gl.glCompileShader(fragment)
gl.glAttachShader(program, vertex)
gl.glAttachShader(program, fragment)
gl.glLinkProgram(program)
gl.glDetachShader(program, vertex)
gl.glDetachShader(program, fragment)
gl.glUseProgram(program)

# Build vertex buffer
# --------------------------------------
n = 10000
data = np.zeros(n, dtype=[('lifetime', np.float32, 1),
                          ('start',    np.float32, 3),
                          ('end',      np.float32, 3)])
vbuffer = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbuffer)
gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_DYNAMIC_DRAW)

# Bind buffer attributes
# --------------------------------------
stride = data.strides[0]

offset = ctypes.c_void_p(0)
loc = gl.glGetAttribLocation(program, "lifetime")
gl.glEnableVertexAttribArray(loc)
gl.glVertexAttribPointer(loc, 1, gl.GL_FLOAT, False, stride, offset)

offset = ctypes.c_void_p(data.dtype["lifetime"].itemsize)
loc = gl.glGetAttribLocation(program, "start")
gl.glEnableVertexAttribArray(loc)
gl.glVertexAttribPointer(loc, 3, gl.GL_FLOAT, False, stride, offset)

offset = ctypes.c_void_p(data.dtype["start"].itemsize)
loc = gl.glGetAttribLocation(program, "end")
gl.glEnableVertexAttribArray(loc)
gl.glVertexAttribPointer(loc, 3, gl.GL_FLOAT, False, stride, offset)


# OpenGL initalization
# --------------------------------------
elapsed_time = 0
gl.glClearColor(0, 0, 0, 1)
gl.glDisable(gl.GL_DEPTH_TEST)
gl.glEnable(gl.GL_BLEND)
gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)
gl.glEnable(gl.GL_VERTEX_PROGRAM_POINT_SIZE)
gl.glEnable(gl.GL_POINT_SPRITE)
new_explosion()

# Enter mainloop
# --------------------------------------
glut.glutMainLoop()
