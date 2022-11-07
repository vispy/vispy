# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Custom Visual for instanced rendering of a colored quad
=======================================================

# this example is based on the tutorial: T01_basic_visual.py
"""

from vispy import app, gloo, visuals, scene, use
import numpy as np

# full gl+ context is required for instanced rendering
use(gl='gl+')


vertex_shader = """
// both these attributes will be defined on an instance basis (not per vertex)
attribute vec2 shift;
attribute vec4 color;

varying vec4 v_color;
void main() {
    v_color = color;
    gl_Position = $transform(vec4($position + shift, 0, 1));
}
"""

fragment_shader = """
varying vec4 v_color;

void main() {
  gl_FragColor = v_color;
}
"""


class InstancedRectVisual(visuals.Visual):
    def __init__(self, x, y, w, h):
        visuals.Visual.__init__(self, vertex_shader, fragment_shader)

        # vertices for two triangles forming a rectangle
        self.vbo = gloo.VertexBuffer(np.array([
            [x, y], [x+w, y], [x+w, y+h],
            [x, y], [x+w, y+h], [x, y+h]
        ], dtype=np.float32))

        self.shared_program.vert['position'] = self.vbo
        self._draw_mode = 'triangles'

        # create a vertex buffer with a divisor argument of 1. This means that the
        # attribute value is set to the next element of the array every 1 instance.
        # The length of the array multiplied by the divisor determines the number
        # of instances
        self.shifts = gloo.VertexBuffer(np.random.rand(100, 2).astype(np.float32) * 500, divisor=1)
        self.shared_program['shift'] = self.shifts

        # we can provide additional buffers with different divisors, as long as the
        # amount of instances (length * divisor) is the same. In this case, we will change
        # color every 5 instances
        self.color = gloo.VertexBuffer(np.random.rand(20, 4).astype(np.float32), divisor=5)
        self.shared_program['color'] = self.color

    def _prepare_transforms(self, view):
        view.view_program.vert['transform'] = view.get_transform()


# create a visual node class to add it to the canvas
InstancedRect = scene.visuals.create_visual_node(InstancedRectVisual)

canvas = scene.SceneCanvas(keys='interactive', show=True)

rect = InstancedRect(0, 0, 20, 40, parent=canvas.scene)

if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        app.run()
