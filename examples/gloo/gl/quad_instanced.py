# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Displaying quads using Instanced rendering
==========================================

This example is a modification of examples/tutorial/gl/quad.py which
uses instanced rendering to generate many copies of the same quad.
"""
import numpy as np

from vispy import app, use
from vispy.gloo import gl

# we need full gl context for instanced rendering
use(gl='gl+')

vertex_code = """
    uniform float scale;
    attribute vec4 color;
    attribute vec2 position;
    attribute vec2 instance_offset;
    varying vec4 v_color;
    void main()
    {
        gl_Position = vec4(scale*position + instance_offset, 0.0, 1.0);
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

        self.n_instances = 1000
        self.instances = np.empty(
            self.n_instances, [("instance_offset", np.float32, 2)]
        )
        self.instances['instance_offset'] = (np.random.rand(self.n_instances, 2) - 0.5) * 2

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
        instance_offset = 0
        loc = gl.glGetAttribLocation(program, "position")
        gl.glEnableVertexAttribArray(loc)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buf)
        gl.glVertexAttribPointer(loc, 3, gl.GL_FLOAT, False, stride, instance_offset)

        instance_offset = self.data.dtype["position"].itemsize
        loc = gl.glGetAttribLocation(program, "color")
        gl.glEnableVertexAttribArray(loc)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buf)
        gl.glVertexAttribPointer(loc, 4, gl.GL_FLOAT, False, stride, instance_offset)

        # instance buffer
        buf = gl.glCreateBuffer()
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buf)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.instances, gl.GL_STATIC_DRAW)
        stride = self.instances.strides[0]
        instance_offset = 0
        loc = gl.glGetAttribLocation(program, "instance_offset")
        gl.glEnableVertexAttribArray(loc)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buf)
        gl.glVertexAttribPointer(loc, 2, gl.GL_FLOAT, False, stride, instance_offset)
        # this is the magic that says "step by 1 every instance"
        gl.glVertexAttribDivisor(loc, 1)

        # Bind uniforms
        # --------------------------------------
        loc = gl.glGetUniformLocation(program, "scale")
        gl.glUniform1f(loc, 0.01)

    def on_draw(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        # you need to call the instanced version of the draw call
        gl.glDrawArraysInstanced(gl.GL_TRIANGLE_STRIP, 0, 4, self.n_instances)

    def on_resize(self, event):
        gl.glViewport(0, 0, *event.physical_size)

if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
