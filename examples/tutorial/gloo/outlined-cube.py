# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Nicolas P .Rougier
# Date:   04/03/2014
# -----------------------------------------------------------------------------
import sys
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut

from vispy.gloo import Program, VertexBuffer, IndexBuffer
from transforms import perspective, translate, rotate
from cube import cube

vertex = """
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform vec4 u_color;
attribute vec3 position;
attribute vec4 color;
varying vec4 v_color;
void main()
{
    v_color = u_color * color;
    gl_Position = u_projection * u_view * u_model * vec4(position,1.0);
}
"""

fragment = """
varying vec4 v_color;
void main()
{
    gl_FragColor = v_color;
}
"""


def display():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    # Filled cube
    gl.glDisable(gl.GL_BLEND)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_POLYGON_OFFSET_FILL)
    program['u_color'] = 1,1,1,1
    program.draw(gl.GL_TRIANGLES, faces)

    # Outlined cube
    gl.glDisable(gl.GL_POLYGON_OFFSET_FILL)
    gl.glEnable(gl.GL_BLEND)
    gl.glDepthMask(gl.GL_FALSE)
    program['u_color'] = 0,0,0,1
    program.draw(gl.GL_LINES, outline)
    gl.glDepthMask(gl.GL_TRUE)

    glut.glutSwapBuffers()

def reshape(width,height):
    gl.glViewport(0, 0, width, height)
    projection = perspective( 45.0, width/float(height), 2.0, 10.0 )
    program['u_projection'] = projection

def keyboard(key, x, y):
    if key == '\033': sys.exit( )

def timer(fps):
    global theta, phi
    theta += .5
    phi += .5
    model = np.eye(4, dtype=np.float32)
    rotate(model, theta, 0,0,1)
    rotate(model, phi, 0,1,0)
    program['u_model'] = model
    glut.glutTimerFunc(1000/fps, timer, fps)
    glut.glutPostRedisplay()


# Glut init
# --------------------------------------
glut.glutInit(sys.argv)
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
glut.glutCreateWindow('Rotating Cube')
glut.glutReshapeWindow(512,512)
glut.glutReshapeFunc(reshape)
glut.glutKeyboardFunc(keyboard )
glut.glutDisplayFunc(display)
glut.glutTimerFunc(1000/60, timer, 60)

# Build cube data
# --------------------------------------
V,I,O = cube()
vertices = VertexBuffer(V)
faces = IndexBuffer(I)
outline = IndexBuffer(O)

# Build program
# --------------------------------------
program = Program(vertex, fragment)
program.bind(vertices)

# Build view, model, projection & normal
# --------------------------------------
view = np.eye(4,dtype=np.float32)
model = np.eye(4,dtype=np.float32)
projection = np.eye(4,dtype=np.float32)
translate(view, 0,0,-5)
program['u_model'] = model
program['u_view'] = view
phi, theta = 0,0

# OpenGL initalization
# --------------------------------------
gl.glClearColor(0.30, 0.30, 0.35, 1.00)
gl.glEnable(gl.GL_DEPTH_TEST)
gl.glPolygonOffset(1, 1)
gl.glEnable(gl.GL_LINE_SMOOTH)
gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
gl.glLineWidth(0.75)

# Start
# --------------------------------------
glut.glutMainLoop()
