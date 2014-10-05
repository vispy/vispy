# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of PointsVisual.
"""

import numpy as np
from vispy import app, gloo, visuals
from vispy.visuals.modular_point import ModularPoint

# vertex positions of data to draw
N = 200
pos = np.zeros((N, 3), dtype=np.float32)
pos[:, 0] = np.linspace(50., 750., N)
pos[:, 1] = np.random.normal(size=N, scale=100, loc=400).astype(np.float32)


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, keys='interactive')
        self.points = ModularPoint(pos, color=(0, 1, 0, 1))
        self.tr_sys = visuals.transforms.TransformSystem(self)
        self.size = (800, 800)
        self.show()

    def on_draw(self, ev):
        gloo.set_clear_color('black')
        gloo.clear(color=True, depth=True)
        gloo.set_viewport(0, 0, *self.size)
        self.points.draw(self.tr_sys)


if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        app.run()
