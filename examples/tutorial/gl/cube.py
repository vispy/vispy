# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Nicolas P .Rougier
# Date:   04/03/2014
# -----------------------------------------------------------------------------
import sys
import math
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut


def checkerboard(grid_num=8, grid_size=32):
    row_even = grid_num / 2 * [0, 1]
    row_odd = grid_num / 2 * [1, 0]
    Z = np.row_stack(grid_num / 2 * (row_even, row_odd)).astype(np.uint8)
    return 255 * Z.repeat(grid_size, axis=0).repeat(grid_size, axis=1)


def rotate(M, angle, x, y, z, point=None):
    angle = math.pi * angle / 180
    c, s = math.cos(angle), math.sin(angle)
    n = math.sqrt(x * x + y * y + z * z)
    x /= n
    y /= n
    z /= n
    cx, cy, cz = (1 - c) * x, (1 - c) * y, (1 - c) * z
    R = np.array([[cx * x + c, cy * x - z * s, cz * x + y * s, 0],
                  [cx * y + z * s, cy * y + c, cz * y - x * s, 0],
                  [cx * z - y * s, cy * z + x * s, cz * z + c, 0],
                  [0, 0, 0, 1]], dtype=M.dtype).T
    M[...] = np.dot(M, R)
    return M


def translate(M, x, y=None, z=None):
    y = x if y is None else y
    z = x if z is None else z
    T = np.array([[1.0, 0.0, 0.0, x],
                  [0.0, 1.0, 0.0, y],
                  [0.0, 0.0, 1.0, z],
                  [0.0, 0.0, 0.0, 1.0]], dtype=M.dtype).T
    M[...] = np.dot(M, T)
    return M


def frustum(left, right, bottom, top, znear, zfar):
    M = np.zeros((4, 4), dtype=np.float32)
    M[0, 0] = +2.0 * znear / (right - left)
    M[2, 0] = (right + left) / (right - left)
    M[1, 1] = +2.0 * znear / (top - bottom)
    M[3, 1] = (top + bottom) / (top - bottom)
    M[2, 2] = -(zfar + znear) / (zfar - znear)
    M[3, 2] = -2.0 * znear * zfar / (zfar - znear)
    M[2, 3] = -1.0
    return M


def perspective(fovy, aspect, znear, zfar):
    h = math.tan(fovy / 360.0 * math.pi) * znear
    w = h * aspect
    return frustum(-w, w, -h, h, znear, zfar)


def makecube():
    """ Generate vertices & indices for a filled cube """

    vtype = [('a_position', np.float32, 3),
             ('a_texcoord', np.float32, 2)]
    itype = np.uint32

    # Vertices positions
    p = np.array([[1, 1, 1], [-1, 1, 1], [-1, -1, 1], [1, -1, 1],
                  [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, -1]])

    # Texture coords
    t = np.array([[0, 0], [0, 1], [1, 1], [1, 0]])

    faces_p = [0, 1, 2, 3, 0, 3, 4, 5, 0, 5, 6,
               1, 1, 6, 7, 2, 7, 4, 3, 2, 4, 7, 6, 5]
    faces_t = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2,
               3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]

    vertices = np.zeros(24, vtype)
    vertices['a_position'] = p[faces_p]
    vertices['a_texcoord'] = t[faces_t]

    indices = np.resize(
        np.array([0, 1, 2, 0, 2, 3], dtype=itype), 6 * (2 * 3))
    indices += np.repeat(4 * np.arange(6), 6)

    return vertices, indices


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


def display():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glDrawElements(
        gl.GL_TRIANGLES, icube_data.size, gl.GL_UNSIGNED_INT, None)
    glut.glutSwapBuffers()


def reshape(width, height):
    gl.glViewport(0, 0, width, height)
    projection = perspective(35.0, width / float(height), 2.0, 10.0)
    loc = gl.glGetUniformLocation(cube, "u_projection")
    gl.glUniformMatrix4fv(loc, 1, False, projection)


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
    loc = gl.glGetUniformLocation(cube, "u_model")
    gl.glUniformMatrix4fv(loc, 1, False, model)
    glut.glutTimerFunc(1000 / fps, timer, fps)
    glut.glutPostRedisplay()


# GLUT init
# --------------------------------------
glut.glutInit()
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
glut.glutCreateWindow('Rotating cube (GL version)')
glut.glutReshapeWindow(512, 512)
glut.glutReshapeFunc(reshape)
glut.glutDisplayFunc(display)
glut.glutKeyboardFunc(keyboard)
glut.glutTimerFunc(1000 / 60, timer, 60)

# Build & activate cube program
# --------------------------------------
cube = gl.glCreateProgram()
vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
gl.glShaderSource(vertex, cube_vertex)
gl.glShaderSource(fragment, cube_fragment)
gl.glCompileShader(vertex)
gl.glCompileShader(fragment)
gl.glAttachShader(cube, vertex)
gl.glAttachShader(cube, fragment)
gl.glLinkProgram(cube)
gl.glDetachShader(cube, vertex)
gl.glDetachShader(cube, fragment)
gl.glUseProgram(cube)

# Get data & build cube buffers
# --------------------------------------
vcube_data, icube_data = makecube()
vcube = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vcube)
gl.glBufferData(
    gl.GL_ARRAY_BUFFER, vcube_data.nbytes, vcube_data, gl.GL_STATIC_DRAW)
icube = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, icube)
gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                icube_data.nbytes, icube_data, gl.GL_STATIC_DRAW)

# Bind cube attributes
# --------------------------------------
stride = vcube_data.strides[0]
offset = ctypes.c_void_p(0)
loc = gl.glGetAttribLocation(cube, "a_position")
gl.glEnableVertexAttribArray(loc)
gl.glVertexAttribPointer(loc, 3, gl.GL_FLOAT, False, stride, offset)

offset = ctypes.c_void_p(vcube_data.dtype["a_position"].itemsize)
loc = gl.glGetAttribLocation(cube, "a_texcoord")
gl.glEnableVertexAttribArray(loc)
gl.glVertexAttribPointer(loc, 2, gl.GL_FLOAT, False, stride, offset)

# Create & bind cube texture
# --------------------------------------
crate = checkerboard()
texture = gl.glGenTextures(1)
gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_INTENSITY,
                crate.shape[1], crate.shape[0],
                0, gl.GL_RED, gl.GL_UNSIGNED_BYTE, crate)
loc = gl.glGetUniformLocation(cube, "u_texture")
gl.glUniform1i(loc, texture)
gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

# Create & bind cube matrices
# --------------------------------------
view = np.eye(4, dtype=np.float32)
model = np.eye(4, dtype=np.float32)
projection = np.eye(4, dtype=np.float32)
translate(view, 0, 0, -7)
phi, theta = 60, 20
rotate(model, theta, 0, 0, 1)
rotate(model, phi, 0, 1, 0)
loc = gl.glGetUniformLocation(cube, "u_model")
gl.glUniformMatrix4fv(loc, 1, False, model)
loc = gl.glGetUniformLocation(cube, "u_view")
gl.glUniformMatrix4fv(loc, 1, False, view)
loc = gl.glGetUniformLocation(cube, "u_projection")
gl.glUniformMatrix4fv(loc, 1, False, projection)

# OpenGL initalization
# --------------------------------------
gl.glClearColor(0.30, 0.30, 0.35, 1.00)
gl.glEnable(gl.GL_DEPTH_TEST)

# Enter mainloop
# --------------------------------------
glut.glutMainLoop()
