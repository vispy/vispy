# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Demonstration of various features of Line visual.
"""
import itertools
import numpy as np

import vispy.app
from vispy import app
from vispy.color import colormaps
from vispy.scene import visuals
from vispy.scene.transforms import STTransform

colormaps = itertools.cycle(colormaps)

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
                                         size=(400, 200), show=True)
        # Create several visuals demonstrating different features of Line
        color = colormaps.next()
        self.line = visuals.Line(pos=pos, color=color, mode='gl')
        self.line.transform = STTransform(translate=[0, 140])
        # redraw the canvas if any visuals request an update
        self.line.parent = self.central_widget
        self.text = visuals.Text(color, bold=True, font_size=24, color='w',
                                 pos=(200, 40), parent=self.central_widget)

        self._timer = vispy.app.Timer(1.0, connect=self.on_timer, start=True)

    # ---------------------------------
    def on_timer(self, event):
        color = colormaps.next()
        self.line.set_data(pos=pos, color=color)
        self.text.text = color
        self.update()


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
