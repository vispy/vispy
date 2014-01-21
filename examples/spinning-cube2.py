#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 50
"""
Show spinning cube using VBO's, and transforms, and texturing.
"""

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

        self.timer = app.Timer(1.0 / 60)
        self.timer.connect(self.update_transforms)
        self.timer.start()

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

    def update_transforms(self, event):
        self.theta += .5
        self.phi += .5
        self.model = np.eye(4, dtype=np.float32)
        rotate(self.model, self.theta, 0, 0, 1)
        rotate(self.model, self.phi, 0, 1, 0)
        self.program['u_model'] = self.model
        self.update()


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
