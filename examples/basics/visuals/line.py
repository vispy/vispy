# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Demonstration of various features of Line visual.
"""
import sys
import numpy as np

import vispy.app
from vispy.scene import visuals
from vispy.scene.transforms import STTransform

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
connect[N/2, 1] = N/2  # put a break in the middle


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        vispy.scene.SceneCanvas.__init__(self, keys='interactive',
                                         size=(800, 800), show=True)
        # Create several visuals demonstrating different features of Line
        self.lines = [
            # agg-mode lines:
            visuals.Line(pos=pos, color=color, mode='agg'),  # per-vertex color
            visuals.Line(pos=pos, color=(0, 0.5, 0.3, 1), mode='agg'),  # solid
            visuals.Line(pos=pos, color=color, width=5, mode='agg'),  # wide
            # GL-mode lines:
            visuals.Line(pos=pos, color=color, mode='gl'),
            visuals.Line(pos=pos, color=(0, 0.5, 0.3, 1), mode='gl'),
            visuals.Line(pos=pos, color=color, width=5, mode='gl'),
            # GL-mode: "connect" not available in AGG mode yet
            
            visuals.Line(pos=pos, color=(0, 0.5, 0.3, 1), connect='segments',
                         mode='gl'),  # only connect alternate vert pairs
            visuals.Line(pos=pos, color=(0, 0.5, 0.3, 1), connect=connect,
                         mode='gl'),  # connect specific pairs
        ]
        counts = [0, 0]
        for i, line in enumerate(self.lines):
            # arrange lines in a grid
            tidx = (line.mode == 'agg')
            x = 400 * tidx
            y = 140 * (counts[tidx] + 1)
            counts[tidx] += 1
            line.transform = STTransform(translate=[x, y])
            # redraw the canvas if any visuals request an update
            line.events.update.connect(lambda evt: self.update())
            line.parent = self.central_widget
        self.texts = [visuals.Text('GL', bold=True, font_size=24, color='w',
                                   pos=(200, 40), parent=self.central_widget),
                      visuals.Text('Agg', bold=True, font_size=24, color='w',
                                   pos=(600, 40), parent=self.central_widget)]


if __name__ == '__main__':
    win = Canvas()

    def update(ev):
        pos[:, 1] = np.random.normal(size=N, scale=30, loc=0)
        win.lines[0].set_data(pos)
        win.lines[3].set_data(pos)

    timer = vispy.app.Timer()
    timer.connect(update)
    timer.start(0)

    if sys.flags.interactive != 1:
        vispy.app.run()
