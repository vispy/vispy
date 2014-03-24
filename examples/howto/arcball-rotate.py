#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 50
"""
Show spinning cube using VBO's, and transforms, and texturing along with 
mouse arcball interaction.
"""

import math

import numpy as np
from vispy import app, gloo, dataio
from vispy.util.transforms import perspective, translate
from vispy.util.transforms import quaternion, qproduct, qmatrix
from vispy.gloo import gl
from vispy.util.cube import cube


VERT_CODE = """
uniform   mat4 u_model;
uniform   mat4 u_view;
uniform   mat4 u_projection;

attribute vec3 position;
attribute vec2 texcoord;

varying vec2 v_texcoord;

void main()
{
    v_texcoord = texcoord;
    gl_Position = u_projection * u_view * u_model * vec4(position, 1.0);
}
"""


FRAG_CODE = """
uniform sampler2D u_texture;
varying vec2 v_texcoord;

void main()
{
    float ty = v_texcoord.y;
    float tx = sin(ty*50.0)*0.01 + v_texcoord.x;
    gl_FragColor = texture2D(u_texture, vec2(tx, ty));
}
"""


# Build cube data
V, I, _ = cube()


class Canvas(app.Canvas):

    def __init__(self, **kwargs):
        app.Canvas.__init__(self, **kwargs)
        self.geometry = 0, 0, 400, 400

        self.indices = gloo.IndexBuffer(I)
        self.vertices = gloo.VertexBuffer(V)

        self.program = gloo.Program(VERT_CODE, FRAG_CODE)
        self.program.bind(self.vertices)

        # Set attributes
        self.program['u_texture'] = gloo.Texture2D(dataio.crate())

        # Handle transformations
        self.init_transforms()

    def on_initialize(self, event):
        gl.glClearColor(1, 1, 1, 1)
        gl.glEnable(gl.GL_DEPTH_TEST)

    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)
        self.projection = perspective(45.0, width / float(height), 2.0, 10.0)
        self.program['u_projection'] = self.projection

    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        self.program.draw(gl.GL_TRIANGLES, self.indices)

    def init_transforms(self):
        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        self.phi = 0
        self.rotation = quaternion()

        translate(self.view, 0, 0, -5)
        self.program['u_model'] = self.model
        self.program['u_view'] = self.view

    def on_mouse_move(self, event):
        if event.is_dragging:
            start = event.last_event.pos
            end = event.pos

            if start == end:
                return

            start = self.get_arcball_vector(start)
            end = self.get_arcball_vector(end)
            self.rotation = qproduct(self.rotation, start, end)
            self.model = np.eye(4, dtype=np.float32)
            self.model = np.dot(self.model, qmatrix(self.rotation))
            self.program['u_model'] = self.model
            self.update()

    def get_arcball_vector(self, vec):
        """
        Converts the x,y screen coordinates to [-1,1] coordinates and then use
        the Pythagorean theorem to check the length of the result vector and
        compute the z coordinate
        """
        radius = min(*self.size)
        result = np.array([0.0, float(vec[0])*2.0 - self.size[0],
                          -float(vec[1])*2.0 + self.size[1], 0.0],
                          dtype=np.float64)
        result /= radius
        result2 = result[1]*result[1]+result[2]*result[2]

        if result2 <= 1:
            result[3] = math.sqrt(1. - result2)
        else:
            result = result/math.sqrt(result2)
        return result


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
