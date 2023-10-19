# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Nicolas P .Rougier
# Date:   04/03/2014
# -----------------------------------------------------------------------------
"""
Drawing a simple quad
=====================
"""
import numpy as np

from vispy import app
from vispy.gloo import gl

vertex_code = """
    uniform float scale;
    attribute vec4 color;
    attribute vec2 position;
    varying vec4 v_color;
    void main()
    {
        gl_Position = vec4(scale*position, 0.0, 1.0);
        v_color = color;
    } """

fragment_code = """
    varying vec4 v_color;
    void main()
    {
        gl_FragColor = v_color;
    } """


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(512, 512), title='Quad (GL)',
                            keys='interactive')

    def on_initialize(self, event):
        # Build data
        self.data = np.zeros(4, [("position", np.float32, 2),
                                 ("color", np.float32, 4)])
        self.data['color'] = [(1, 0, 0, 1), (0, 1, 0, 1),
                              (0, 0, 1, 1), (1, 1, 0, 1)]
        self.data['position'] = [(-1, -1), (-1, +1),
                                 (+1, -1), (+1, +1)]

        # Build & activate program

        # Request a program and shader slots from GPU
        program = gl.glCreateProgram()
        vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

        # Set shaders source
        gl.glShaderSource(vertex, vertex_code)
        gl.glShaderSource(fragment, fragment_code)

        # Compile shaders
        gl.glCompileShader(vertex)
        gl.glCompileShader(fragment)

        # Attach shader objects to the program
        gl.glAttachShader(program, vertex)
        gl.glAttachShader(program, fragment)

        # Build program
        gl.glLinkProgram(program)

        # Get rid of shaders (no more needed)
        gl.glDetachShader(program, vertex)
        gl.glDetachShader(program, fragment)

        # Make program the default program
        gl.glUseProgram(program)

        # Build buffer

        # Request a buffer slot from GPU
        buf = gl.glCreateBuffer()

        # Make this buffer the default one
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buf)

        # Upload data
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.data, gl.GL_DYNAMIC_DRAW)

        # Bind attributes
        stride = self.data.strides[0]
        offset = 0
        loc = gl.glGetAttribLocation(program, "position")
        gl.glEnableVertexAttribArray(loc)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buf)
        gl.glVertexAttribPointer(loc, 3, gl.GL_FLOAT, False, stride, offset)

        offset = self.data.dtype["position"].itemsize
        loc = gl.glGetAttribLocation(program, "color")
        gl.glEnableVertexAttribArray(loc)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buf)
        gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, False, stride, offset)

        # Bind uniforms
        # --------------------------------------
        loc = gl.glGetUniformLocation(program, "scale")
        gl.glUniform1f(loc, 1.0)

    def on_draw(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

    def on_resize(self, event):
        gl.glViewport(0, 0, *event.physical_size)

if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
