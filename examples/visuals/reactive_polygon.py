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
pos = [[0, 0, 0],
       [0.25, 0.22, 0],
       [0.25, 0.5, 0],
       [0, 0.5, 0],
       [-0.25, 0.25, 0]]


class Canvas(vispy.app.Canvas):
    def __init__(self):
        self.polygon = visuals.Polygon(pos=pos, color=(1, 0, 0, 1),
                                       border_color=(1, 1, 1, 1))
        
        vispy.app.Canvas.__init__(self, close_keys='escape')
        self.pos = np.array(pos)
        self.i = 1
        self.size = (800, 800)
        self.show()

        self.timer = vispy.app.Timer(1.0 / 60)  # change rendering speed here
        self.timer.connect(self.on_timer)
        self.timer.start()

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
        gloo.set_viewport(0, 0, *self.size)
        self.polygon.draw()
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
