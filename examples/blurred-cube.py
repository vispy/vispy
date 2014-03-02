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
from vispy.gloo import Program, VertexBuffer, IndexBuffer, Texture2D
from vispy.gloo import FrameBuffer, DepthBuffer
from vispy.util.transforms import perspective, translate, rotate

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
    // Inverse video
    if( v_texcoord.x > 0.5 ) {
        gl_FragColor.rgb = 1.0 - texture2D(u_texture, v_texcoord).rgb;
    } else {
        gl_FragColor = texture2D(u_texture, v_texcoord);
    }
}
"""


def display():

    framebuffer.activate()
    gl.glDrawBuffer(gl.GL_COLOR_ATTACHMENT0)
    gl.glViewport(0, 0, 512, 512)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glEnable(gl.GL_DEPTH_TEST)
    cube.draw(gl.GL_TRIANGLES, indices)
    gl.glDrawBuffer(gl.GL_NONE)
    framebuffer.deactivate()

    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glDisable(gl.GL_DEPTH_TEST)
    quad.draw(gl.GL_TRIANGLE_STRIP)

    glut.glutSwapBuffers()


def reshape(width, height):
    gl.glViewport(0, 0, width, height)
    projection = perspective(30.0, width / float(height), 2.0, 10.0)
    cube['u_projection'] = projection


def keyboard(key, x, y):
    if key == '\033':
        sys.exit()


def timer(fps):
    global theta, phi
    theta += .5
    phi += .5
    model = np.eye(4, dtype=np.float32)
    rotate(model, theta, 0, 0, 1)
    rotate(model, phi, 0, 1, 0)
    cube['u_model'] = model
    glut.glutTimerFunc(1000 / fps, timer, fps)
    glut.glutPostRedisplay()


# Glut init
# --------------------------------------
glut.glutInit(sys.argv)
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
glut.glutCreateWindow('Framebuffer rendering')
glut.glutReshapeWindow(512, 512)
glut.glutReshapeFunc(reshape)
glut.glutKeyboardFunc(keyboard)
glut.glutDisplayFunc(display)
glut.glutTimerFunc(1000 / 60, timer, 60)

# Build cube data
# --------------------------------------
vertices, indices, _ = cube.cube()
vertices = VertexBuffer(vertices)
indices = IndexBuffer(indices)

# Build program
# --------------------------------------
view = np.eye(4, dtype=np.float32)
model = np.eye(4, dtype=np.float32)
projection = np.eye(4, dtype=np.float32)
translate(view, 0, 0, -7)
phi, theta = 60, 20
rotate(model, theta, 0, 0, 1)
rotate(model, phi, 0, 1, 0)

cube = Program(cube_vertex, cube_fragment)
cube.bind(vertices)
cube["u_texture"] = np.load("crate.npy")
cube["u_texture"].interpolation = gl.GL_LINEAR
cube['u_model'] = model
cube['u_view'] = view

depth = DepthBuffer((512, 512))
color = Texture2D(shape=(512, 512, 3), dtype=np.dtype(np.float32))
framebuffer = FrameBuffer(color=color, depth=depth)

quad = Program(quad_vertex, quad_fragment, count=4)
quad['a_texcoord'] = [(0, 0), (0, 1), (1, 0), (1, 1)]
quad['a_position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
quad['u_texture'] = color
quad["u_texture"].interpolation = gl.GL_LINEAR

# OpenGL initalization
# --------------------------------------
gl.glClearColor(.3, .3, .35, 1)
gl.glEnable(gl.GL_DEPTH_TEST)

# Start
# --------------------------------------
glut.glutMainLoop()
