# -*- coding: utf-8 -*-
# vispy: testskip (KNOWNFAIL)
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of LinePlot visual.
"""

import numpy as np
import sys

import vispy.app
from vispy.scene import visuals

# vertex positions of data to draw
N = 20
pos = np.zeros((N, 2), dtype=np.float32)
pos[:, 0] = np.linspace(10, 790, N)
pos[:, 1] = np.random.normal(size=N, scale=100, loc=400)


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        self.line = visuals.LinePlot(pos, color='w', edge_color='w',
                                     face_color=(0.2, 0.2, 1))
        vispy.scene.SceneCanvas.__init__(self, keys='interactive',
                                         size=(800, 800), show=True)
        self.line.parent = self.scene


if __name__ == '__main__':
    win = Canvas()
    if sys.flags.interactive != 1:
        vispy.app.run()
