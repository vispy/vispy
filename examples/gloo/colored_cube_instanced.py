# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Nicolas P .Rougier, Lorenzo Gaifas
# Date:   04/03/2014
# -----------------------------------------------------------------------------
"""
Draw many colored cubes using instanced rendering
=================================================
"""

import numpy as np

from vispy import app, gloo, use
from vispy.gloo import Program, VertexBuffer, IndexBuffer
from vispy.util.transforms import perspective, translate, rotate
from vispy.geometry import create_cube

use(gl='gl+')

vertex = """
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

// per-vertex attributes
attribute vec3 position;
attribute vec2 texcoord;
attribute vec3 normal;
attribute vec4 color; // unused (it's returned by generate_cube() but we don't need it)

// per-instance attributes
attribute vec3 instance_shift;
attribute vec3 instance_color;

varying vec4 v_color;
void main()
{
    v_color = vec4(instance_color, 1);
    gl_Position = projection * view * model * vec4(position + instance_shift,1.0);
}
"""

fragment = """
varying vec4 v_color;
void main()
{
    gl_FragColor = v_color;
}
"""


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(512, 512), title='Colored instanced cube',
                            keys='interactive')

        # Build cube data
        V, I, _ = create_cube()
        vertices = VertexBuffer(V)
        self.indices = IndexBuffer(I)

        instance_shift = VertexBuffer(((np.random.rand(100, 3) - 0.5) * 50).astype(np.float32), divisor=1)
        instance_color = VertexBuffer(np.random.rand(5, 3).astype(np.float32), divisor=20)

        # Build program
        self.program = Program(vertex, fragment)
        self.program.bind(vertices)

        # Build view, model, projection & normal
        view = translate((0, 0, -100))
        model = np.eye(4, dtype=np.float32)
        self.program['model'] = model
        self.program['view'] = view
        self.program['instance_shift'] = instance_shift
        self.program['instance_color'] = instance_color
        self.phi, self.theta = 0, 0
        gloo.set_state(clear_color=(0.30, 0.30, 0.35, 1.00), depth_test=True)

        self.activate_zoom()

        self.timer = app.Timer('auto', self.on_timer, start=True)

        self.show()

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        self.program.draw('triangles', self.indices)

    def on_resize(self, event):
        self.activate_zoom()

    def activate_zoom(self):
        gloo.set_viewport(0, 0, *self.physical_size)
        projection = perspective(45.0, self.size[0] / float(self.size[1]),
                                 2.0, 200.0)
        self.program['projection'] = projection

    def on_timer(self, event):
        self.theta += .5
        self.phi += .5
        self.program['model'] = np.dot(rotate(self.theta, (0, 0, 1)),
                                       rotate(self.phi, (0, 1, 0)))
        self.update()

if __name__ == '__main__':
    c = Canvas()
    app.run()
