#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 50
"""
Show spinning cube using VBO's, and transforms, and texturing.
"""

import math

import numpy as np
from vispy import app, gloo, dataio
from vispy.util.transforms import perspective, translate, rotate
from vispy.gloo import gl


VERT_CODE = """
uniform   mat4 u_model;
uniform   mat4 u_view;
uniform   mat4 u_projection;

attribute vec3 a_position;
attribute vec2 a_texcoord;

varying vec2 v_texcoord;

void main()
{
    v_texcoord = a_texcoord;
    gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
    //gl_Position = vec4(a_position,1.0);
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


# Read cube data
positions, faces, normals, texcoords = dataio.read_mesh('cube.obj')
colors = np.random.uniform(0, 1, positions.shape).astype('float32')

faces_buffer = gloo.ElementBuffer(faces.astype(np.uint16))


class Canvas(app.Canvas):

    def __init__(self, **kwargs):
        app.Canvas.__init__(self, **kwargs)
        self.geometry = 0, 0, 400, 400

        self.program = gloo.Program(VERT_CODE, FRAG_CODE)

        # Set attributes
        self.program['a_position'] = gloo.VertexBuffer(positions)
        self.program['a_texcoord'] = gloo.VertexBuffer(texcoords)

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

        self.program.draw(gl.GL_TRIANGLES, faces_buffer)

    def init_transforms(self):
        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        self.theta = 0
        self.phi = 0

        translate(self.view, 0, 0, -5)
        self.program['u_model'] = self.model
        self.program['u_view'] = self.view

    def on_mouse_move(self, event):
        if event.is_dragging:
            start = event.last_event.pos
            end = event.pos

            if start==end: return

            start = self.get_arcball_vector(start)
            end = self.get_arcball_vector(end)
            self.theta = math.acos(min(1.0, np.dot(start,end)))/5
            axis_camera = np.cross(start,end)
            rotate(self.model, self.theta*180/math.pi, axis_camera[0], axis_camera[1], axis_camera[2])
            self.program['u_model'] = self.model
            self.update()


    def get_arcball_vector(self, vec):
        """
        Convert the x,y screen coordinates to [-1,1] coordinates and then use
        the Pythagorean theorem to check the length of the result vector and
        compute the z coordinate
        """
        result = np.array([float(vec[0])/self.size[0]*2.0 - 1.0,
                            -float(vec[1])/self.size[1]*2.0 + 1.0, 0.0],
                            dtype=np.float32)
        result2 = np.linalg.norm(result)

        if result2<=1:
            result[2] = math.sqrt(1 - result2)
        else:
            result = result/result2

        return result

                


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
