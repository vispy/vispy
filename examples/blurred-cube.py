#! /usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import sys
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut

import cube
from vispy.gloo import Program, VertexBuffer, IndexBuffer, Texture2D, FrameBuffer
from vispy.gloo import FrameBuffer, ColorBuffer, DepthBuffer, StencilBuffer
from vispy.util.transforms import perspective, translate, rotate

# from vispy.util import set_log_level
# set_log_level("debug")


cube_vertex = """
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
attribute vec3 a_position;
attribute vec2 a_texcoord;
varying vec2 v_texcoord;
void main()
{
    gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
    v_texcoord = a_texcoord;
}
"""

cube_fragment = """
uniform sampler2D u_texture;
varying vec2 v_texcoord;
void main()
{
    gl_FragColor = texture2D(u_texture, v_texcoord);
}
"""

quad_vertex = """
attribute vec2 a_position;
attribute vec2 a_texcoord;
varying vec2 v_texcoord;
void main()
{
    gl_Position = vec4(a_position, 0.0, 1.0);
    v_texcoord = a_texcoord;
}
"""

quad_fragment = """
uniform sampler2D u_texture;
varying vec2 v_texcoord;
void main()
{
    if( v_texcoord.x > 0.5 )
        gl_FragColor = texture2D(u_texture, v_texcoord);
    else
        gl_FragColor = vec4(vec3(.25),1.0) + 0.75*texture2D(u_texture, v_texcoord);
}
"""



def display():

    if 1:
        framebuffer.activate()
        gl.glDrawBuffer(gl.GL_COLOR_ATTACHMENT0)
        gl.glViewport(0, 0, 512, 512)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)
        cube.draw(gl.GL_TRIANGLES, indices)
        framebuffer.deactivate()

        gl.glClear(gl.GL_COLOR_BUFFER_BIT) # | gl.GL_DEPTH_BUFFER_BIT)
        gl.glDisable(gl.GL_DEPTH_TEST)
        quad.draw(gl.GL_TRIANGLE_STRIP)

    else:
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        cube.draw(gl.GL_TRIANGLES, indices)

    glut.glutSwapBuffers()

def reshape(width,height):
    gl.glViewport(0, 0, width, height)
    projection = perspective( 35.0, width/float(height), 2.0, 10.0 )
    cube['u_projection'] = projection

def keyboard(key, x, y):
    if key == '\033':
        sys.exit( )
    if key == ' ':
        screenshot('screenshot.png')

def timer(fps):
    global theta, phi
    theta += .5
    phi += .5
    model = np.eye(4, dtype=np.float32)
    rotate(model, theta, 0,0,1)
    rotate(model, phi, 0,1,0)
    cube['u_model'] = model
    glut.glutTimerFunc(1000/fps, timer, fps)
    glut.glutPostRedisplay()


# Glut init
# --------------------------------------
glut.glutInit(sys.argv)
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
glut.glutCreateWindow('Blurred textured Cube')
glut.glutReshapeWindow(512,512)
glut.glutReshapeFunc(reshape)
glut.glutKeyboardFunc(keyboard )
glut.glutDisplayFunc(display)
glut.glutTimerFunc(1000/60, timer, 60)

# Build cube data
# --------------------------------------
vertices, indices, _ = cube.cube()
vertices = VertexBuffer(vertices)
indices = IndexBuffer(indices)

# Build program
# --------------------------------------
view = np.eye(4,dtype=np.float32)
model = np.eye(4,dtype=np.float32)
projection = np.eye(4,dtype=np.float32)
translate(view, 0,0,-7)
phi, theta = 60,20
rotate(model, theta, 0,0,1)
rotate(model, phi, 0,1,0)

cube = Program(cube_vertex, cube_fragment)
cube.bind(vertices)
cube["u_texture"] = np.load("crate.npy")
cube["u_texture"].interpolation = gl.GL_LINEAR
cube['u_model'] = model
cube['u_view'] = view

quad = Program(quad_vertex, quad_fragment, count=4)
quad['a_texcoord'] = [ ( 0, 0), ( 0, 1), ( 1, 0), ( 1, 1) ]
quad['a_position'] = [ (-1,-1), (-1,+1), (+1,-1), (+1,+1) ]

depth = DepthBuffer((512,512))
color = Texture2D(shape=(512,512,3), dtype=np.dtype(np.float32))
#depth = Texture2D(shape=(512,512,1), dtype=np.dtype(np.float32),
#                  format=gl.GL_DEPTH_COMPONENT)
quad['u_texture'] = color
quad["u_texture"].interpolation = gl.GL_LINEAR

framebuffer = FrameBuffer(color=color, depth=depth)



# OpenGL initalization
# --------------------------------------
gl.glClearColor( .3, .3, .35, 1 )
gl.glEnable(gl.GL_DEPTH_TEST)

# Start
# --------------------------------------
glut.glutMainLoop()
