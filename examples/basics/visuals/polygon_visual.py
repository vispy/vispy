# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of PolygonVisual. 
"""

import numpy as np
import vispy.app
from vispy import gloo
from vispy.scene import visuals

# vertex positions of data to draw
pos = np.array([[0, 0, 0],
               [0.25, 0.22, 0],
               [0.25, 0.5, 0],
               [0, 0.5, 0],
               [-0.25, 0.25, 0]])

pos = np.array([[0, 0],
                [10, 0],
                [10, 10],
                [20, 10],
                [20, 20],
                [25, 20],
                [25, 25],
                [20, 25],
                [20, 20],
                [10, 17],
                [5, 25],
                [9, 30],
                [6, 15],
                [15, 12.5],
                [0, 5]])

theta = np.linspace(0, 2*np.pi, 11)
pos = np.hstack([np.cos(theta)[:,np.newaxis], 
                 np.sin(theta)[:,np.newaxis]])
pos[::2] *= 0.4
pos[-1] = pos[0]

class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        global pos
        
        self.polygon = visuals.Polygon(pos=pos, color=(1, 0, 0, 1),
                                       border_color=(1, 1, 1, 1))
        self.polygon.transform = vispy.scene.transforms.STTransform(
            scale=(300, 300),
            translate=(400, 400))
        vispy.scene.SceneCanvas.__init__(self, keys='interactive')
        self.size = (800, 800)
        self.show()
        
    def on_draw(self, ev):
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        self.draw_visual(self.polygon)
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
