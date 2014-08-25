# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of PlotLine visual.
"""

import numpy as np
import vispy.app
from vispy import gloo
from vispy.scene import visuals
from vispy.scene.transforms import STTransform

# vertex positions of data to draw
N = 20
pos = np.zeros((N, 2), dtype=np.float32)
pos[:, 0] = np.linspace(10, 790, N)
pos[:, 1] = np.random.normal(size=N, scale=100, loc=400)



class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        
        self.line = visuals.PlotLine(pos, color=(1, 1, 1, 1), 
                                     edge_color=(1, 1, 1, 1), 
                                     face_color=(0.2, 0.2, 1, 1))

        vispy.scene.SceneCanvas.__init__(self, keys='interactive')
        self.size = (800, 800)
        self.show()

    def on_draw(self, ev):
        gloo.set_clear_color('black')
        gloo.clear(color=True, depth=True)
        self.draw_visual(self.line)


if __name__ == '__main__':
    win = Canvas()

    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
