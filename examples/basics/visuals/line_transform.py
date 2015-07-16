# -*- coding: utf-8 -*-
# vispy: gallery 1
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstration of Line visual with arbitrary transforms.

Several Line visuals are displayed that all have the same vertex position
information, but different transformations.
"""

import numpy as np
from vispy import app, gloo, visuals
from vispy.visuals.transforms import (STTransform, LogTransform,
                                      MatrixTransform, PolarTransform)
import vispy.util
vispy.util.use_log_level('debug')

# vertex positions of data to draw
N = 200
pos = np.zeros((N, 2), dtype=np.float32)
pos[:, 0] = np.linspace(-350, 350, N)
pos[:, 1] = np.random.normal(size=N, scale=50, loc=0)

# One array of colors
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=(800, 800))

        # Define several Line visuals that use the same position data
        # but have different colors and transformations
        colors = [color, (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1),
                  (1, 1, 0, 1), (1, 1, 1, 1)]

        self.lines = [visuals.LineVisual(pos=pos, color=colors[i])
                      for i in range(6)]

        center = STTransform(translate=(400, 400))

        self.lines[0].transform = center

        self.lines[1].transform = (center *
                                   STTransform(scale=(1, 0.1, 1)))

        self.lines[2].transform = (center *
                                   STTransform(translate=(200, 200, 0)) *
                                   STTransform(scale=(0.3, 0.5, 1)))

        self.lines[3].transform = (center *
                                   STTransform(translate=(-200, -200, 0),
                                               scale=(200, 1)) *
                                   LogTransform(base=(10, 0, 0)) *
                                   STTransform(translate=(1, 0, 0)))

        self.lines[4].transform = MatrixTransform()
        self.lines[4].transform.rotate(45, (0, 0, 1))
        self.lines[4].transform.scale((0.3, 0.3, 1))
        self.lines[4].transform.translate((200, 200, 0))

        self.lines[5].transform = (STTransform(translate=(200, 600, 0),
                                               scale=(5, 5)) *
                                   PolarTransform() *
                                   LogTransform(base=(2, 0, 0)) *
                                   STTransform(scale=(0.01, 0.1),
                                               translate=(4, 20)))

        self.show()

    def on_draw(self, ev):
        gloo.clear('black', depth=True)
        for line in self.lines:
            line.draw()
            
    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        for line in self.lines:
            line.transforms.configure(canvas=self, viewport=vp)

if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        app.run()
