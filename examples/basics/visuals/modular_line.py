# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of LineVisual.
"""

import numpy as np
from vispy import app, gloo, visuals
from vispy.visuals.modular_line import ModularLine

# vertex positions of data to draw
N = 200
pos = np.zeros((N, 3), dtype=np.float32)
pos[:, 0] = np.linspace(100, 700, N)
pos[:, 1] = np.random.normal(size=N, scale=100, loc=400)

# color array
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]


class Canvas(app.Canvas):
    def __init__(self):
        self.line = ModularLine(pos=pos, color=color)
        app.Canvas.__init__(self, keys='interactive')
        self.size = (800, 800)
        self.tr_sys = visuals.transforms.TransformSystem(self)
        self.show()

    def on_draw(self, ev):
        gloo.set_clear_color('black')
        gloo.clear(color=True, depth=True)
        gloo.set_viewport(0, 0, *self.size)
        self.line.draw(self.tr_sys)


if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        app.run()
