# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import sys
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
from vispy.gloo import Program, VertexBuffer, IndexBuffer

vertex = """
    attribute vec2 position;
    attribute vec2 texcoord;
    varying vec2 v_texcoord;
    void main()
    {
        gl_Position = vec4(position, 0.0, 1.0);
        v_texcoord = texcoord;
    } """

fragment = """
    uniform sampler2D texture;
    varying vec2 v_texcoord;
    void main()
    {
        gl_FragColor = texture2D(texture, v_texcoord);
    } """

def checkerboard(grid_num=8, grid_size=32):
    row_even = grid_num/2 * [0,1]
    row_odd = grid_num/2 * [1,0]
    Z = np.row_stack(grid_num/2*(row_even, row_odd)).astype(np.uint8)
    return 255*Z.repeat(grid_size, axis = 0).repeat(grid_size, axis = 1)

def display():
    gl.glClearColor(1,1,1,1)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    program.draw(gl.GL_TRIANGLE_STRIP)
    glut.glutSwapBuffers()

def reshape(width,height):
    gl.glViewport(0, 0, width, height)

def keyboard( key, x, y ):
    if key == '\033':
        sys.exit( )

# Glut init
# --------------------------------------
glut.glutInit(sys.argv)
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
glut.glutCreateWindow('Textured quad')
glut.glutReshapeWindow(512,512)
glut.glutReshapeFunc(reshape)
glut.glutKeyboardFunc(keyboard )
glut.glutDisplayFunc(display)

# Build program & data
# ----------------------------------------
program = Program(vertex, fragment, count=4)
program['position'] = [ (-1,-1),   (-1,+1),   (+1,-1),   (+1,+1)   ]
program['texcoord'] = [ (0,0), (1,0), (0,1), (1,1) ]
program['texture'] = checkerboard()

# Enter mainloop
# --------------------------------------
glut.glutMainLoop()
