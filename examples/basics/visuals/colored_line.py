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

import vispy
from vispy import app
from vispy.color import colormaps
from vispy.scene import visuals
from vispy.scene.transforms import STTransform
from vispy.ext.six import next

colormaps = itertools.cycle(colormaps)

# vertex positions of data to draw
N = 200
pos = np.zeros((N, 2), dtype=np.float32)
pos[:, 0] = np.linspace(10, 390, N)
pos[:, 1] = np.random.normal(size=N, scale=20, loc=0)


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        vispy.scene.SceneCanvas.__init__(self, keys='interactive',
                                         size=(400, 200), show=True)
        # Create a visual that updates the line with different colormaps
        color = next(colormaps)
        self.line = visuals.Line(pos=pos, color=color, mode='gl')
        self.line.transform = STTransform(translate=[0, 140])
        # redraw the canvas if the visual requests an update
        self.line.parent = self.central_widget
        self.text = visuals.Text(color, bold=True, font_size=24, color='w',
                                 pos=(200, 40), parent=self.central_widget)

        self._timer = app.Timer(2.0, connect=self.on_timer, start=True)

    # ---------------------------------
    def on_timer(self, event):
        color = next(colormaps)
        self.line.set_data(pos=pos, color=color)
        self.text.text = color
        self.update()


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
