# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstration of animated Line visual.
"""

import numpy as np
import vispy.app
from vispy.scene import visuals

# vertex positions of data to draw
N = 200
pos = np.zeros((N, 2), dtype=np.float32)
pos[:, 0] = np.linspace(50., 750., N)
pos[:, 1] = np.random.normal(size=N, scale=100, loc=400)

# color array
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        vispy.scene.SceneCanvas.__init__(self, keys='interactive',
                                         size=(800, 800), show=True)
        self.line = visuals.Line(pos, color, parent=self.scene)
        self.line.events.update.connect(lambda evt: self.update)


if __name__ == '__main__':
    win = Canvas()

    def update(ev):
        pos[:, 1] = np.random.normal(size=N, scale=100, loc=400)
        win.line.set_data(pos=pos)

    timer = vispy.app.Timer()
    timer.connect(update)
    timer.start(0)

    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
