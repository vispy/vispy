#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
This example shows how to use the `ArrowVisual` for a quiver plot
"""

import sys
import math
import itertools

import numpy as np
from vispy import app, gloo, visuals
from vispy.visuals.transforms import NullTransform
from vispy.util import transforms

class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, title="Quiver plot", keys="interactive",
                            size=(830, 430))

        self.arrow_length = 20

        self.num_rows = 8
        self.num_cols = 16

        self.line_vertices = []

        # Generate grid
        for i, j in itertools.product(range(self.num_rows),
                                      range(self.num_cols)):
            x = 25 + (50 * j)
            y = 25 + (50 * i)

            coords = np.array([x, y])

            # Initial line vertices, all arrows point upwards
            self.line_vertices.extend([
                coords + np.array([0, 0.5*self.arrow_length]),
                coords - np.array([0, 0.5*self.arrow_length])
            ])

        self.line_vertices = np.array(self.line_vertices)

        self.visual = visuals.ArrowVisual(
            pos=self.line_vertices,
            color='white',
            connect='segments',
            arrow_size=8,
            arrows=self.line_vertices.reshape((len(self.line_vertices)/2, 4))
        )

        self.visual.events.update.connect(lambda evt: self.update())
        self.visual.transform = NullTransform()

        self.show()

    def on_draw(self, event):
        gloo.clear('black')
        self.visual.draw()

    def on_resize(self, event):
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        self.visual.transforms.configure(canvas=self, viewport=vp)

    def on_mouse_move(self, event):
        # Keep original line vertices so we can always apply the rotation
        # matrix on the original vertices, and we don't have to think about
        # relative corners etc.
        new_line_vertices = np.zeros_like(self.line_vertices)
        vertices_iter = iter(self.line_vertices)
        for i, v1 in enumerate(vertices_iter):
            v2 = next(vertices_iter)

            center = v1 - np.array([0, 0.5*self.arrow_length])
            center = np.append(center, [0.0])
            direction_vect = (np.array([event.pos[0], event.pos[1], 0.0]) -
                              center)
            direction_vect /= np.linalg.norm(direction_vect)
            print(direction_vect)

            angle = math.degrees(math.acos(direction_vect[0]))
            print(angle)
            rot_matrix = transforms.rotate(angle, center)
            v1 = np.append(v1, [0.0, 1.0]).T.dot(rot_matrix)
            v2 = np.append(v2, [0.0, 1.0]).T.dot(rot_matrix)

            new_line_vertices[i*2] = v1[0:2]
            new_line_vertices[(i*2)+1] = v2[0:2]

        self.visual.set_data(
            new_line_vertices,
            arrows=new_line_vertices.reshape((len(new_line_vertices)/2, 4))
        )


if __name__ == '__main__':
    win = Canvas()

    if sys.flags.interactive != 1:
        app.run()
