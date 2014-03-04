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

vertex = """
    uniform float theta;
    attribute vec4 color;
    attribute vec2 position;
    varying vec4 v_color;
    void main()
    {
        float ct = cos(theta);
        float st = sin(theta);
        float x = 0.75* (position.x*ct - position.y*st);
        float y = 0.75* (position.x*st + position.y*ct);
        gl_Position = vec4(x, y, 0.0, 1.0);
        v_color = color;
    } """

fragment = """
    varying vec4 v_color;
    void main()
    {
        gl_FragColor = v_color;
    } """

def display():
    gl.glClearColor(1,1,1,1)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    program.draw(gl.GL_TRIANGLE_STRIP)
    glut.glutSwapBuffers()

def reshape(width,height):
    gl.glViewport(0, 0, width, height)

def keyboard( key, x, y ):
    if key == '\033': sys.exit( )

def timer(fps):
    global clock
    clock += 0.001 * 1000.0/fps
    program['theta'] = clock
    glut.glutTimerFunc(1000/fps, timer, fps)
    glut.glutPostRedisplay()

# Glut init
# --------------------------------------
glut.glutInit(sys.argv)
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
glut.glutCreateWindow('Hello world!')
glut.glutReshapeWindow(512,512)
glut.glutReshapeFunc(reshape)
glut.glutKeyboardFunc(keyboard )
glut.glutDisplayFunc(display)
glut.glutTimerFunc(1000/60, timer, 60)

# Build program & data
# ----------------------------------------
program = Program(vertex, fragment, count=4)
program['color']    = [ (1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1) ]
program['position'] = [ (-1,-1),   (-1,+1),   (+1,-1),   (+1,+1)   ]
clock = 0

# Enter mainloop
# --------------------------------------
glut.glutMainLoop()
