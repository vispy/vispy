# !/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

from vispy import gloo
from vispy import app
from vispy.util.transforms import perspective, translate, rotate


vert = """
uniform   mat4 u_model;
uniform   mat4 u_view;
uniform   mat4 u_projection;
uniform   vec4 u_color;
attribute vec3 a_position;
attribute vec3 a_normal;
varying vec3 v_normal;

void main (void)
{
    v_normal = a_position;
    gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
}
"""

frag = """
uniform samplerCube u_cube;
varying vec3 v_normal;

void main()
{
    vec3 color = (textureCube(u_cube, v_normal).rgb);
    gl_FragColor = vec4(color, 1.0);
}
"""


def cube():
    """
    Build vertices for a colored cube.

    V  is the vertices
    I1 is the indices for a filled cube (use with GL_TRIANGLES)
    I2 is the indices for an outline cube (use with GL_LINES)
    """
    vtype = [('a_position', np.float32, 3),
             ('a_normal', np.float32, 3)]
    # Vertices positions
    v = [[1, 1, 1], [-1, 1, 1], [-1, -1, 1], [1, -1, 1],
         [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, -1]]
    # Face Normals
    n = [[0, 0, 1], [1, 0, 0], [0, 1, 0],
         [-1, 0, 1], [0, -1, 0], [0, 0, -1]]

    V = np.array([
        (v[0], n[0]), (v[1], n[0]),
        (v[2], n[0]), (v[3], n[0]),
        (v[0], n[1]), (v[3], n[1]),
        (v[4], n[1]), (v[5], n[1]),
        (v[0], n[2]), (v[5], n[2]),
        (v[6], n[2]), (v[1], n[2]),
        (v[1], n[3]), (v[6], n[3]),
        (v[7], n[3]), (v[2], n[3]),
        (v[7], n[4]), (v[4], n[4]),
        (v[3], n[4]), (v[2], n[4]),
        (v[4], n[5]), (v[7], n[5]),
        (v[6], n[5]), (v[5], n[5])],
        dtype=vtype)
    I1 = np.resize(np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32), 6 * (2 * 3))
    I1 += np.repeat(4 * np.arange(2 * 3, dtype=np.uint32), 6)

    I2 = np.resize(
        np.array([0, 1, 1, 2, 2, 3, 3, 0], dtype=np.uint32), 6 * (2 * 4))
    I2 += np.repeat(4 * np.arange(6, dtype=np.uint32), 8)

    return V, I1, I2


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=(800, 600))

        self.vertices, self.filled, self.outline = cube()
        self.filled_buf = gloo.IndexBuffer(self.filled)
        self.outline_buf = gloo.IndexBuffer(self.outline)

        self.program = gloo.Program(vert, frag)
        self.program.bind(gloo.VertexBuffer(self.vertices))

        self.view = translate((0, 0, -5))
        self.model = np.eye(4, dtype=np.float32)

        gloo.set_viewport(0, 0, self.physical_size[0], self.physical_size[1])
        self.projection = perspective(45.0, self.size[0] /
                                      float(self.size[1]), 2.0, 10.0)

        self.program['u_projection'] = self.projection

        self.program['u_model'] = self.model
        self.program['u_view'] = self.view

        ones = np.ones((32, 32), dtype=np.float32)
        zero = np.zeros((32, 32), dtype=np.float32)
        cube_faces = np.stack([
            np.dstack((zero, zero, ones)),
            np.dstack((ones, zero, zero)),
            np.dstack((zero, ones, zero)),
            np.dstack((zero, ones, ones)),
            np.dstack((ones, zero, ones)),
            np.dstack((ones, ones, zero)),
        ], axis=0)
        self.program['u_cube'] = gloo.TextureCubeMap(
            cube_faces, interpolation='linear', wrapping='clamp_to_edge',
            internalformat='rgb32f')

        self.theta = 0
        self.phi = 0

        gloo.set_clear_color('white')
        gloo.set_state('opaque')
        gloo.set_polygon_offset(1, 1)

        self._timer = app.Timer('auto', connect=self.on_timer, start=True)

        self.show()

    def on_timer(self, event):
        self.theta += .5
        self.phi += 0.5
        self.model = np.dot(rotate(self.theta, (0, 1, 0)),
                            rotate(self.phi, (0, 0, 1)))
        self.program['u_model'] = self.model
        self.update()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, event.physical_size[0], event.physical_size[1])
        self.projection = perspective(45.0, event.size[0] /
                                      float(event.size[1]), 2.0, 10.0)
        self.program['u_projection'] = self.projection

    def on_draw(self, event):
        gloo.clear()
        gloo.set_state(blend=False, depth_test=True, polygon_offset_fill=True)
        self.program.draw('triangles', self.filled_buf)


if __name__ == '__main__':
    c = Canvas()
    app.run()

