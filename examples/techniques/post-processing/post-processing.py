# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author:   Nicolas P .Rougier
# Date:     04/03/2014
# Abstract: Show post-processing technique using framebuffer
# Keywords: framebuffer, gloo, cube, post-processing
# -----------------------------------------------------------------------------
import sys
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut

import cube
from transforms import perspective, translate, rotate
from vispy.gloo import Program, VertexBuffer, IndexBuffer, Texture2D
from vispy.gloo import FrameBuffer, DepthBuffer

cube_vertex = """
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
attribute vec3 position;
attribute vec2 texcoord;
varying vec2 v_texcoord;
void main()
{
    gl_Position = projection * view * model * vec4(position,1.0);
    v_texcoord = texcoord;
}
"""

cube_fragment = """
uniform sampler2D texture;
varying vec2 v_texcoord;
void main()
{
    float r = texture2D(texture, v_texcoord).r;
    gl_FragColor = vec4(r,r,r,1);
}
"""

quad_vertex = """
attribute vec2 position;
attribute vec2 texcoord;
varying vec2 v_texcoord;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
    v_texcoord = texcoord;
}
"""

quad_fragment = """
uniform sampler2D texture;
varying vec2 v_texcoord;
void main()
{
    vec2 d = 5.0 * vec2(sin(v_texcoord.y*50.0),0)/512.0;

    // Inverse video
    if( v_texcoord.x > 0.5 ) {
        gl_FragColor.rgb = 1.0-texture2D(texture, v_texcoord+d).rgb;
    } else {
        gl_FragColor = texture2D(texture, v_texcoord);
    }
}
"""


def checkerboard(grid_num=8, grid_size=32):
    row_even = grid_num / 2 * [0, 1]
    row_odd = grid_num / 2 * [1, 0]
    Z = np.row_stack(grid_num / 2 * (row_even, row_odd)).astype(np.uint8)
    return 255 * Z.repeat(grid_size, axis=0).repeat(grid_size, axis=1)


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
    cube['projection'] = projection


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
    cube['model'] = model
    glut.glutTimerFunc(1000 / fps, timer, fps)
    glut.glutPostRedisplay()


# Glut init
# --------------------------------------
glut.glutInit(sys.argv)
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
glut.glutCreateWindow('Framebuffer post-processing')
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
cube["texture"] = checkerboard()
cube["texture"].interpolation = gl.GL_LINEAR
cube['model'] = model
cube['view'] = view

depth = DepthBuffer((512, 512))
color = Texture2D(shape=(512, 512, 3), dtype=np.dtype(np.float32))
framebuffer = FrameBuffer(color=color, depth=depth)

quad = Program(quad_vertex, quad_fragment, count=4)
quad['texcoord'] = [(0, 0), (0, 1), (1, 0), (1, 1)]
quad['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
quad['texture'] = color
quad["texture"].interpolation = gl.GL_LINEAR

# OpenGL initalization
# --------------------------------------
gl.glClearColor(.3, .3, .35, 1)
gl.glEnable(gl.GL_DEPTH_TEST)

# Start
# --------------------------------------
glut.glutMainLoop()
