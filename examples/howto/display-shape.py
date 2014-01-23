# !/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 2

"""
Simple example demonstrating showing a quad.
gloo objects that this example demonstrates: Program.
"""

from vispy import gloo
from vispy import app
from vispy.gloo import gl
import numpy as np

# Create vetices
vPosition = np.array([[-0.8, -0.8, 0.0], [+0.7, -0.7, 0.0],
                      [-0.7, +0.7, 0.0], [+0.8, +0.8, 0.0, ]], np.float32)


VERT_SHADER = """ // simple vertex shader
attribute vec3 a_position;
void main (void) {
    gl_Position = vec4(a_position, 1.0);
}
"""

FRAG_SHADER = """ // simple fragment shader
uniform vec4 u_color;
void main()
{
    gl_FragColor = u_color;
}
"""


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self)

        # Create program
        self._program = gloo.Program(VERT_SHADER, FRAG_SHADER)

        # Set uniform and attribute
        self._program['u_color'] = 0.2, 1.0, 0.4, 1
        self._program['a_position'] = gloo.VertexBuffer(vPosition)

    def on_initialize(self, event):
        gl.glClearColor(1, 1, 1, 1)

    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)

    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self._program.draw(gl.GL_TRIANGLE_STRIP)


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
