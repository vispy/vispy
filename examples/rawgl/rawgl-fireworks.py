#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This example is equivalent to the fireworks example,
but does not use vispy.gloo, but the raw GL API.

Example demonstrating simulation of fireworks using point sprites.
(adapted from the "OpenGL ES 2.0 Programming Guide")

This example demonstrates a series of explosions that last one second. The
visualization during the explosion is highly optimized using a Vertex Buffer
Object (VBO). After each explosion, vertex data for the next explosion are
calculated, such that each explostion is unique.
"""

import time
import numpy as np
import ctypes

from vispy import app
from vispy.gloo import gl


# Create a texture
radius = 32
im1 = np.random.normal(0.8, 0.3, (radius * 2 + 1, radius * 2 + 1))

# Mask it with a disk
L = np.linspace(-radius, radius, 2 * radius + 1)
(X, Y) = np.meshgrid(L, L)
im1 *= np.array((X ** 2 + Y ** 2) <= radius * radius, dtype='float32')

# Set number of particles, you should be able to scale this to 100000
N = 10000

# Create vertex data container
vertex_data = np.zeros((N,), dtype=[('a_lifetime', np.float32, 1),
                                    ('a_startPosition', np.float32, 3),
                                    ('a_endPosition', np.float32, 3)])


VERT_CODE = """
uniform float u_time;
uniform vec3 u_centerPosition;
attribute float a_lifetime;
attribute vec3 a_startPosition;
attribute vec3 a_endPosition;
varying float v_lifetime;

void main () {
    if (u_time <= a_lifetime)
    {
        gl_Position.xyz = a_startPosition + (u_time * a_endPosition);
        gl_Position.xyz += u_centerPosition;
        gl_Position.y -= 1.0 * u_time * u_time;
        gl_Position.w = 1.0;
    }
    else
        gl_Position = vec4(-1000, -1000, 0, 0);

    v_lifetime = 1.0 - (u_time / a_lifetime);
    v_lifetime = clamp(v_lifetime, 0.0, 1.0);
    gl_PointSize = (v_lifetime * v_lifetime) * 40.0;
}
"""

FRAG_CODE = """
uniform sampler2D s_texture;
uniform vec4 u_color;
varying float v_lifetime;

void main()
{
    vec4 texColor;
    texColor = texture2D(s_texture, gl_PointCoord);
    gl_FragColor = vec4(u_color) * texColor;
    gl_FragColor.a *= v_lifetime;
}
"""


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self)
        self.size = 400, 400
        self._starttime = time.time()
        self._new_explosion()

    def on_initialize(self, event):
        gl.glClearColor(0, 0, 0, 1)

        # Enable blending
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)

        # Create shader program
        self._prog_handle = gl.glCreateProgram()

        # Create vertex shader
        shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource_compat(shader, VERT_CODE)
        gl.glCompileShader(shader)
        status = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
        if not status:
            # We could show more useful info here, but that takes a few lines
            raise RuntimeError('Vertex shader did not compile.')
        else:
            gl.glAttachShader(self._prog_handle, shader)

        # Create fragment shader
        shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        need_enabled = gl.glShaderSource_compat(shader, FRAG_CODE)
        gl.glCompileShader(shader)
        status = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
        if not status:
            # We could show more useful info here, but that takes a few lines
            raise RuntimeError('Fragment shader did not compile.')
        else:
            gl.glAttachShader(self._prog_handle, shader)

        # Enable point sprites
        for enum in need_enabled:
            gl.glEnable(enum)

        # Link
        gl.glLinkProgram(self._prog_handle)
        status = gl.glGetProgramiv(self._prog_handle, gl.GL_LINK_STATUS)
        if not status:
            # We could show more useful info here, but that takes a few lines
            raise RuntimeError('Program did not link.')

        # Create texture
        self._tex_handle = gl.glGenTextures(1)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._tex_handle)
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,
            0,
            gl.GL_LUMINANCE,
            im1.shape[1],
            im1.shape[0],
            0,
            gl.GL_LUMINANCE,
            gl.GL_FLOAT,
            im1.astype(
                np.float32))
        gl.glTexParameter(
            gl.GL_TEXTURE_2D,
            gl.GL_TEXTURE_MIN_FILTER,
            gl.GL_LINEAR)
        gl.glTexParameter(
            gl.GL_TEXTURE_2D,
            gl.GL_TEXTURE_MAG_FILTER,
            gl.GL_LINEAR)

        # Create vertex buffer
        self._vbo_handle = gl.glGenBuffers(1)

    def on_paint(self, event):

        # Technically, we would only need to set u_time on every draw,
        # because the program is enabled at the beginning and never disabled.
        # In vispy, the program is re-enabled at each draw though and we
        # want to keep the code similar.

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Activate program  and texture
        gl.glUseProgram(self._prog_handle)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._tex_handle)

        # Update VBO
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._vbo_handle)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            vertex_data.nbytes,
            vertex_data,
            gl.GL_DYNAMIC_DRAW)

        # Set attributes (again, the loc can be cached)
        loc = gl.glGetAttribLocation(
            self._prog_handle,
            'a_lifetime'.encode('utf-8'))
        gl.glEnableVertexAttribArray(loc)
        gl.glVertexAttribPointer(
            loc,
            1,
            gl.GL_FLOAT,
            False,
            7 * 4,
            ctypes.c_voidp(0))
        #
        loc = gl.glGetAttribLocation(
            self._prog_handle,
            'a_startPosition'.encode('utf-8'))
        gl.glEnableVertexAttribArray(loc)
        gl.glVertexAttribPointer(
            loc,
            3,
            gl.GL_FLOAT,
            False,
            7 * 4,
            ctypes.c_voidp(
                1 * 4))
        #
        loc = gl.glGetAttribLocation(
            self._prog_handle,
            'a_endPosition'.encode('utf-8'))
        gl.glEnableVertexAttribArray(loc)
        gl.glVertexAttribPointer(
            loc,
            3,
            gl.GL_FLOAT,
            False,
            7 * 4,
            ctypes.c_voidp(
                4 * 4))
        #
        loc = gl.glGetUniformLocation(
            self._prog_handle,
            'u_color'.encode('utf-8'))
        gl.glUniform4f(loc, *self._color)

        # Set unforms
        loc = gl.glGetUniformLocation(
            self._prog_handle,
            'u_time'.encode('utf-8'))
        gl.glUniform1f(loc, time.time() - self._starttime)
        #
        loc = gl.glGetUniformLocation(
            self._prog_handle,
            'u_centerPosition'.encode('utf-8'))
        gl.glUniform3f(loc, *self._centerpos)

        # Draw
        gl.glDrawArrays(gl.GL_POINTS, 0, N)

        # New explosion?
        if time.time() - self._starttime > 1.5:
            self._new_explosion()

        # Redraw as fast as we can
        self.update()

    def _new_explosion(self):
        # New centerpos
        self._centerpos = np.random.uniform(-0.5, 0.5, (3,))

        # New color, scale alpha with N
        alpha = 1.0 / N ** 0.08
        color = np.random.uniform(0.1, 0.9, (3,))
        self._color = tuple(color) + (alpha,)

        # Create new vertex data
        vertex_data['a_lifetime'] = np.random.normal(2.0, 0.5, (N,))
        vertex_data['a_startPosition'] = np.random.normal(0.0, 0.2, (N, 3))
        vertex_data['a_endPosition'] = np.random.normal(0.0, 1.2, (N, 3))

        # Set time to zero
        self._starttime = time.time()


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
