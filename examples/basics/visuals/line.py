# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Demonstration of various features of Line visual.
"""

from __future__ import division

import sys
import numpy as np

from vispy import app, gloo, visuals
from vispy.visuals.transforms import STTransform, NullTransform

# vertex positions of data to draw
N = 200
pos = np.zeros((N, 2), dtype=np.float32)
pos[:, 0] = np.linspace(10, 390, N)
pos[:, 1] = np.random.normal(size=N, scale=20, loc=0)

# color array
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

# connection array
connect = np.empty((N-1, 2), np.int32)
connect[:, 0] = np.arange(N-1)
connect[:, 1] = connect[:, 0] + 1
connect[N//2, 1] = N//2  # put a break in the middle


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, keys='interactive',
                            size=(800, 800))
        # Create several visuals demonstrating different features of Line
        self.lines = [
            # agg-method lines:
            # per-vertex color
            visuals.LineVisual(pos=pos, color=color, method='agg'),
            # solid
            visuals.LineVisual(pos=pos, color=(0, 0.5, 0.3, 1), method='agg'),
            # wide
            visuals.LineVisual(pos=pos, color=color, width=5, method='agg'),

            # GL-method lines:
            visuals.LineVisual(pos=pos, color=color, method='gl'),
            visuals.LineVisual(pos=pos, color=(0, 0.5, 0.3, 1), method='gl'),
            visuals.LineVisual(pos=pos, color=color, width=5, method='gl'),
            # GL-method: "connect" not available in AGG method yet

            # only connect alternate vert pairs
            visuals.LineVisual(pos=pos, color=(0, 0.5, 0.3, 1),
                               connect='segments', method='gl'),
            # connect specific pairs
            visuals.LineVisual(pos=pos, color=(0, 0.5, 0.3, 1),
                               connect=connect, method='gl'),
        ]
        counts = [0, 0]
        for i, line in enumerate(self.lines):
            # arrange lines in a grid
            tidx = (line.method == 'agg')
            x = 400 * tidx
            y = 140 * (counts[tidx] + 1)
            counts[tidx] += 1
            line.transform = STTransform(translate=[x, y])
            # redraw the canvas if any visuals request an update
            line.events.update.connect(lambda evt: self.update())

        self.texts = [visuals.TextVisual('GL', bold=True, font_size=24,
                                         color='w', pos=(200, 40)),
                      visuals.TextVisual('Agg', bold=True, font_size=24,
                                         color='w', pos=(600, 40))]
        for text in self.texts:
            text.transform = NullTransform()
        self.visuals = self.lines + self.texts
        self.show()

    def on_draw(self, event):
        gloo.clear('black')
        for visual in self.visuals:
            visual.draw()

    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        for visual in self.visuals:
            visual.transforms.configure(canvas=self, viewport=vp)


if __name__ == '__main__':
    win = Canvas()

    def update(ev):
        pos[:, 1] = np.random.normal(size=N, scale=30, loc=0)
        for line in win.lines:
            line.set_data(pos)

    timer = app.Timer()
    timer.connect(update)
    timer.start(1.0)

    if sys.flags.interactive != 1:
        app.run()
