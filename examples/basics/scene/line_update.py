# -*- coding: utf-8 -*-
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
x_lim = [50., 750.]
y_lim = [-2., 2.]
pos[:, 0] = np.linspace(x_lim[0], x_lim[1], N)
pos[:, 1] = np.random.normal(size=N)

# color array
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

canvas = scene.SceneCanvas(keys='interactive', show=True)
viewbox = canvas.central_widget.add_view()

# add some axes
domains = np.array([x_lim, y_lim])
pos_ax = [np.array([domains[0], [domains[1][0]] * 2]).T,
          np.array([[domains[0][0]] * 2, domains[1]]).T]
x_axis = scene.Axis(pos_ax[0], domains[0], (0, -1), parent=viewbox.scene)
y_axis = scene.Axis(pos_ax[1], domains[1], (-1, 0), parent=viewbox.scene)

viewbox.camera = 'panzoom'  # set after adding axes to auto-zoom

line = scene.Line(pos, color, parent=viewbox.scene)


def update(ev):
    global pos, color, line
    pos[:, 1] = np.random.normal(size=N)
    color = np.roll(color, 1, axis=0)
    line.set_data(pos=pos, color=color)

timer = app.Timer()
timer.connect(update)
timer.start(0)

if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
