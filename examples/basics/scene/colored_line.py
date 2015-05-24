# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Demonstration of various features of Line visual.
"""
import itertools
import numpy as np

from vispy import app, scene
from vispy.color import get_colormaps
from vispy.visuals.transforms import STTransform
from vispy.ext.six import next

colormaps = itertools.cycle(get_colormaps())

# vertex positions of data to draw
N = 200
pos = np.zeros((N, 2), dtype=np.float32)
pos[:, 0] = np.linspace(10, 390, N)
pos[:, 1] = np.random.normal(size=N, scale=20, loc=0)


canvas = scene.SceneCanvas(keys='interactive', size=(400, 200), show=True)

# Create a visual that updates the line with different colormaps
color = next(colormaps)
line = scene.Line(pos=pos, color=color, method='gl')
line.transform = STTransform(translate=[0, 140])
line.parent = canvas.central_widget

text = scene.Text(color, bold=True, font_size=24, color='w',
                  pos=(200, 40), parent=canvas.central_widget)


def on_timer(event):
    global colormaps, line, text, pos
    color = next(colormaps)
    line.set_data(pos=pos, color=color)
    text.text = color

timer = app.Timer(.5, connect=on_timer, start=True)


if __name__ == '__main__':
    canvas.app.run()
