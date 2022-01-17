# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" Display Windbarbs.
"""

import itertools

import numpy as np
from vispy import app
from vispy.visuals import WindbarbVisual
from vispy.visuals.transforms import NullTransform


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, title="Windbarb plot", keys="interactive",
                            size=(830, 430))

        self.windbarb_length = 25
        self.grid_spacing = 50

        self.grid_coords = None
        self.line_vertices = None
        self.last_mouse = (0, 0)

        self.generate_grid()

        direction_vectors = (self.grid_coords - self.last_mouse).astype(
            np.float32)
        direction_vectors[:] /= 10
        direction_vectors[:, 1] *= -1

        self.visual = WindbarbVisual(pos=self.grid_coords,
                                     wind=direction_vectors,
                                     trig=False,
                                     edge_color='black',
                                     face_color='black',
                                     size=self.windbarb_length)

        self.visual.events.update.connect(lambda evt: self.update())
        self.visual.transform = NullTransform()

        self.show()

    def generate_grid(self):
        n = self.grid_spacing / 2.
        num_cols = int(self.physical_size[0] / n * 2)
        num_rows = int(self.physical_size[1] / n * 2)
        coords = []

        # Generate grid
        for i, j in itertools.product(range(num_rows), range(num_cols)):
            x = n + (n * 2 * j)
            y = n + (n * 2 * i)

            coords.append((x, y))

        self.grid_coords = np.array(coords)

    def on_resize(self, event):
        self.generate_grid()
        self.rotate_arrows(np.array(self.last_mouse))

        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        self.visual.transforms.configure(canvas=self, viewport=vp)

    def rotate_arrows(self, point_towards):
        direction_vectors = (self.grid_coords - point_towards).astype(
            np.float32)
        direction_vectors[:] /= 10
        direction_vectors[:, 1] *= -1

        self.visual.set_data(
            pos=self.grid_coords,
            wind=direction_vectors,
            size=self.windbarb_length,
        )

    def on_mouse_move(self, event):
        self.last_mouse = event.pos
        self.rotate_arrows(np.array(event.pos))

    def on_draw(self, event):
        self.context.clear(color='white')
        self.visual.draw()


if __name__ == '__main__':
    canvas = Canvas()
    canvas.measure_fps()
    app.run()
