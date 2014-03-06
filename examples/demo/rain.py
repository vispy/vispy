# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author:   Nicolas P .Rougier
# Date:     06/03/2014
# Abstract: Water ripple effect following mouse
# Keywords: antialias, water, mouse
# -----------------------------------------------------------------------------
import sys
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut

from vispy.gloo import Program, VertexBuffer
from vispy.util.transforms import ortho

vertex = """
#version 120

uniform mat4  u_model;
uniform mat4  u_view;
uniform mat4  u_projection;
uniform float u_linewidth;
uniform float u_antialias;

attribute vec3  a_position;
attribute vec4  a_fg_color;
attribute float a_size;

varying vec4  v_fg_color;
varying float v_size;

void main (void)
{
    v_size = a_size;
    v_fg_color = a_fg_color;
    if( a_fg_color.a > 0.0)
    {
        gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
        gl_PointSize = v_size + u_linewidth + 2*1.5*u_antialias;
    }
    else
    {
        gl_Position = u_projection * u_view * u_model * vec4(-1,-1,0,1);
        gl_PointSize = 0.0;
    }
}
"""

fragment = """
#version 120

uniform float u_linewidth;
uniform float u_antialias;
varying vec4  v_fg_color;
varying vec4  v_bg_color;
varying float v_size;
float disc(vec2 P, float size)
{
    return length((P.xy - vec2(0.5,0.5))*size);
}
void main()
{
    if( v_fg_color.a <= 0.0)
        discard;
    float actual_size = v_size + u_linewidth + 2*1.5*u_antialias;
    float t = u_linewidth/2.0 - u_antialias;
    float r = disc(gl_PointCoord, actual_size);
    float d = abs(r - v_size/2.0) - t;
    if( d < 0.0 )
    {
         gl_FragColor = v_fg_color;
    }
    else if( abs(d) > 2.5*u_antialias )
    {
         discard;
    }
    else
    {
        d /= u_antialias;
        gl_FragColor = vec4(v_fg_color.rgb, exp(-d*d)*v_fg_color.a);
    }
}
"""


def display():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    program.draw(gl.GL_POINTS)
    glut.glutSwapBuffers()


def reshape(width, height):
    gl.glViewport(0, 0, width, height)
    projection = ortho(0, width, 0, height, -1, +1)
    program['u_projection'] = projection


def keyboard(key, x, y):
    if key == '\033':
        sys.exit()


def timer(fps):
    glut.glutTimerFunc(1000 / fps, timer, fps)
    data['a_fg_color'][..., 3] -= 0.01
    data['a_size'] += 1.0
    vdata.set_data(data)
    glut.glutPostRedisplay()


def on_passive_motion(x, y):
    global index
    _, _, _, h = gl.glGetIntegerv(gl.GL_VIEWPORT)
    data['a_position'][index] = x, h - y
    data['a_size'][index] = 5
    data['a_fg_color'][index] = 0, 0, 0, 1
    index = (index + 1) % 500
    glut.glutPostRedisplay()


# Glut init
# --------------------------------------
glut.glutInit(sys.argv)
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
glut.glutCreateWindow('Rain [Move mouse]')
glut.glutReshapeWindow(512, 512)
glut.glutReshapeFunc(reshape)
glut.glutKeyboardFunc(keyboard)
glut.glutDisplayFunc(display)
glut.glutPassiveMotionFunc(on_passive_motion)
glut.glutTimerFunc(1000 / 60, timer, 60)

# Build data
# --------------------------------------
n = 500
data = np.zeros(n, [('a_position', np.float32, 2),
                    ('a_fg_color', np.float32, 4),
                    ('a_size',     np.float32, 1)])
index = 0

# Build program
# --------------------------------------
program = Program(vertex, fragment)
vdata = VertexBuffer(data)
program.bind(vdata)
program['u_antialias'] = 1.00
program['u_linewidth'] = 1.00

# Build view, model, projection
# --------------------------------------
program['u_model'] = np.eye(4, dtype=np.float32)
program['u_view'] = np.eye(4, dtype=np.float32)

# OpenGL initalization
# --------------------------------------
gl.glClearColor(1.0, 1.0, 1.0, 1.0)
gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
gl.glEnable(gl.GL_BLEND)
gl.glEnable(gl.GL_VERTEX_PROGRAM_POINT_SIZE)
gl.glEnable(gl.GL_POINT_SPRITE)

# Start
# --------------------------------------
glut.glutMainLoop()
