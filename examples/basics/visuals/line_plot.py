# -*- coding: utf-8 -*-
# vispy: testskip (KNOWNFAIL)
# Copyright (c) Vispy Development Team. All Rights Reserved.
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
                                           symbol='o', 
                                           face_color=(0.2, 0.2, 1))
        self.show()

    def on_draw(self, event):
        gloo.clear('black')
        self.line.draw()

    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        self.line.transforms.configure(canvas=self, viewport=vp)

if __name__ == '__main__':
    win = Canvas()
    if sys.flags.interactive != 1:
        app.run()
