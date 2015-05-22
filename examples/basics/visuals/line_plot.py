# -*- coding: utf-8 -*-
# vispy: testskip (KNOWNFAIL)
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of LinePlot visual.
"""

import numpy as np
import sys

from vispy import gloo, app, visuals

# vertex positions of data to draw
N = 20
pos = np.zeros((N, 2), dtype=np.float32)
pos[:, 0] = np.linspace(10, 790, N)
pos[:, 1] = np.random.normal(size=N, scale=100, loc=400)


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, keys='interactive',
                            size=(800, 800))

        self.line = visuals.LinePlotVisual(pos, color='w', edge_color='w',
                                           face_color=(0.2, 0.2, 1))

        self.tr_sys = visuals.transforms.TransformSystem(self)

        self.show()

    def on_draw(self, event):
        gloo.clear('black')
        gloo.set_viewport(0, 0, *self.physical_size)
        self.line.draw(self.tr_sys)


if __name__ == '__main__':
    win = Canvas()
    if sys.flags.interactive != 1:
        app.run()
