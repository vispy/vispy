# -*- coding: utf-8 -*-
# vispy: testskip (KNOWNFAIL)
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstration of LinePlot visual with axes.
"""

# from __future__ import division

import numpy as np
import sys

from vispy import gloo, app, visuals

# size of canvas and graph
canvas_size = (1000, 800)
graph_size = (900, 700)

# vertex positions of data to draw
N = 30

margin_x = (canvas_size[0]-graph_size[0]) / 2.
margin_y = (canvas_size[1]-graph_size[1]) / 2.

extents_x = np.array([[margin_x, canvas_size[1]-margin_y],
                     [canvas_size[0]-margin_x, canvas_size[1]-margin_y]])

extents_y = np.array([[margin_x, canvas_size[1]-margin_y],
                     [margin_x, margin_y]])

pos = np.zeros((N, 2), dtype=np.float32)
pos[:, 0] = np.linspace(margin_x, canvas_size[0]-margin_x, N)
pos[:, 1] = np.clip(np.random.normal(size=N, scale=100, loc=canvas_size[1] / 2.), margin_y, canvas_size[0]-margin_y)


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive',
                            size=canvas_size)

        self.line = visuals.LinePlotVisual(pos, color='w', edge_color='w',
                                           face_color=(0.2, 0.2, 1))

        self.axis_x = visuals.AxisVisual(extents=extents_x, domain=(0, 100))
        self.axis_y = visuals.AxisVisual(extents=extents_y, domain=(5, 7.5))

        self.tr_sys = visuals.transforms.TransformSystem(self)

        self.show()

    def on_draw(self, event):
        gloo.clear('black')
        gloo.set_viewport(0, 0, *self.physical_size)

        self.axis_x.draw(self.tr_sys)
        self.axis_y.draw(self.tr_sys)

        self.line.draw(self.tr_sys)


if __name__ == '__main__':
    win = Canvas()
    if sys.flags.interactive != 1:
        app.run()
