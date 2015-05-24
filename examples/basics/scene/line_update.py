# -*- coding: utf-8 -*-
# vispy: testskip  # disabled due to segfaults on travis
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstration of animated Line visual.
"""

import sys
import numpy as np
from vispy import app, scene

# vertex positions of data to draw
N = 200
pos = np.zeros((N, 2), dtype=np.float32)
pos[:, 0] = np.linspace(50., 750., N)
pos[:, 1] = np.random.normal(size=N, scale=100, loc=400)

# color array
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

canvas = scene.SceneCanvas(keys='interactive', size=(800, 800), show=True)

line = scene.Line(pos, color, parent=canvas.scene)


def update(ev):
    global pos, color, line
    pos[:, 1] = np.random.normal(size=N, scale=100, loc=400)
    color = np.roll(color, 1, axis=0)
    line.set_data(pos=pos, color=color)

timer = app.Timer()
timer.connect(update)
timer.start(0)

if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
