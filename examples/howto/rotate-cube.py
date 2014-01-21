#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 50
"""
This example shows how to display 3D objects.
You should see a colored outlined spinning cube.
"""

import numpy as np
from vispy import app, gloo
from vispy.gloo import gl
from vispy.util.transforms import perspective, translate, rotate


vert = """
// Uniforms
// ------------------------------------
uniform   mat4 u_model;
uniform   mat4 u_view;
uniform   mat4 u_projection;
uniform   vec4 u_color;

// Attributes
// ------------------------------------
attribute vec3 a_position;
attribute vec4 a_color;

// Varying
// ------------------------------------
varying vec4 v_color;

void main()
{
    v_color = a_color * u_color;
    gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
}
"""


frag = """
// Varying
// ------------------------------------
varying vec4 v_color;

void main()
{
    gl_FragColor = v_color;
}
"""


# -----------------------------------------------------------------------------
def cube():
    """
    Build vertices for a colored cube.

    V  is the vertices
    I1 is the indices for a filled cube (use with GL_TRIANGLES)
    I2 is the indices for an outline cube (use with GL_LINES)
    """
    vtype = [('a_position', np.float32, 3),
             ('a_normal', np.float32, 3),
             ('a_color', np.float32, 4)]
    # Vertices positions
    v = [[1, 1, 1], [-1, 1, 1], [-1, -1, 1], [1, -1, 1],
         [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, -1]]
    # Face Normals
    n = [[0, 0, 1], [1, 0, 0], [0, 1, 0],
         [-1, 0, 1], [0, -1, 0], [0, 0, -1]]
    # Vertice colors
    c = [[0, 1, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1], [0, 1, 0, 1],
         [1, 1, 0, 1], [1, 1, 1, 1], [1, 0, 1, 1], [1, 0, 0, 1]]

    V = np.array([(v[0], n[0], c[0]), (v[1], n[0], c[1]),
                  (v[2], n[0], c[2]), (v[3], n[0], c[3]),
                  (v[0], n[1], c[0]), (v[3], n[1], c[3]),
                  (v[4], n[1], c[4]), (v[5], n[1], c[5]),
                  (v[0], n[2], c[0]), (v[5], n[2], c[5]),
                  (v[6], n[2], c[6]), (v[1], n[2], c[1]),
                  (v[1], n[3], c[1]), (v[6], n[3], c[6]),
                  (v[7], n[3], c[7]), (v[2], n[3], c[2]),
                  (v[7], n[4], c[7]), (v[4], n[4], c[4]),
                  (v[3], n[4], c[3]), (v[2], n[4], c[2]),
                  (v[4], n[5], c[4]), (v[7], n[5], c[7]),
                  (v[6], n[5], c[6]), (v[5], n[5], c[5])],
                 dtype=vtype)
    I1 = np.resize(np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32), 6 * (2 * 3))
    I1 += np.repeat(4 * np.arange(2 * 3), 6)

    I2 = np.resize(
        np.array([0, 1, 1, 2, 2, 3, 3, 0], dtype=np.uint32), 6 * (2 * 4))
    I2 += np.repeat(4 * np.arange(6), 8)

    return V, I1, I2


# -----------------------------------------------------------------------------
class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self)
        self.size = 800, 600

        self.vertices, self.filled, self.outline = cube()
        self.filled_buf = gloo.ElementBuffer(self.filled)
        self.outline_buf = gloo.ElementBuffer(self.outline)

        self.program = gloo.Program(vert, frag)
        self.program.set_vars(gloo.VertexBuffer(self.vertices))

        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        translate(self.view, 0, 0, -5)
        self.program['u_model'] = self.model
        self.program['u_view'] = self.view

        self.theta = 0
        self.phi = 0

        self._timer = app.Timer(1.0 / 60)
        self._timer.connect(self.on_timer)
        self._timer.start()

    # ---------------------------------
    def on_initialize(self, event):
        gl.glClearColor(1, 1, 1, 1)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glPolygonOffset(1, 1)
        # gl.glEnable( gl.GL_LINE_SMOOTH )

    # ---------------------------------
    def on_timer(self, event):
        self.theta += .5
        self.phi += .5
        self.model = np.eye(4, dtype=np.float32)
        rotate(self.model, self.theta, 0, 0, 1)
        rotate(self.model, self.phi, 0, 1, 0)
        self.program['u_model'] = self.model
        self.update()

    # ---------------------------------
    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)
        self.projection = perspective(45.0, width / float(height), 2.0, 10.0)
        self.program['u_projection'] = self.projection

    # ---------------------------------
    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        with self.program as prog:
            # Filled cube
            gl.glDisable(gl.GL_BLEND)
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glEnable(gl.GL_POLYGON_OFFSET_FILL)
            prog['u_color'] = 1, 1, 1, 1
            prog.draw(gl.GL_TRIANGLES, self.filled_buf)

            # Outline
            gl.glDisable(gl.GL_POLYGON_OFFSET_FILL)
            gl.glEnable(gl.GL_BLEND)
            gl.glDepthMask(gl.GL_FALSE)
            prog['u_color'] = 0, 0, 0, 1
            prog.draw(gl.GL_LINES, self.outline_buf)
            gl.glDepthMask(gl.GL_TRUE)


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
