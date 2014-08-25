# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of PolygonVisual. 
"""

import numpy as np
import vispy
from vispy import gloo, app
from vispy.scene import visuals

# vertex positions of data to draw
pos = [[0, 0, 0],
       [0.25, 0.22, 0],
       [0.25, 0.5, 0],
       [0, 0.5, 0],
       [-0.25, 0.25, 0]]


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        self.polygon = visuals.Polygon(pos=pos, color=(1, 0, 0, 1),
                                       border_color=(1, 1, 1, 1))
        self.polygon.transform = vispy.scene.transforms.STTransform(
            scale=(500, 500),
            translate=(400, 400))
        
        vispy.scene.SceneCanvas.__init__(self, keys='interactive')
        self.pos = np.array(pos)
        self.i = 1
        self.size = (800, 800)
        self.show()

        self._timer = app.Timer('auto', connect=self.on_timer, start=True)

    def on_timer(self, event):
        self.pos[0] += [self.i, 0.0, 0.0]
        self.i *= -0.92
        self.polygon.pos = self.pos
        self.update()

    def on_mouse_press(self, event):
        self.i = 1.
        self.pos = np.array(pos)
        self.update()

    def on_draw(self, ev):
        gloo.clear(color='black')
        self.draw_visual(self.polygon)
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
