# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of reactive RegularPolygonVisual. 
"""

import vispy.app
from vispy import gloo
from vispy.scene import visuals
import numpy as np


class Canvas(vispy.app.Canvas):
    def __init__(self):
        self.rpolygon = visuals.RegularPolygon(pos=(0.0, 0.0, 0), radius=0.2,
                                               color=(1, 0, 0, 1),
                                               border_color=(1, 1, 1, 1),
                                               sides=4)
        
        vispy.app.Canvas.__init__(self, close_keys='escape')
        self.size = (800, 800)
        self.show()
        
        self.rfactor = 0.01
        self.timer = vispy.app.Timer(1.0 / 10)  # change rendering speed here
        self.timer.connect(self.on_timer)
        self.timer.start()

    def on_timer(self, event):
        if (self.rpolygon.radius > 0.5 or self.rpolygon.radius < 0.2):
            self.rfactor *= -1
        self.rpolygon.radius += self.rfactor
        self.rpolygon.sides += 100*self.rfactor
        self.rpolygon.color = (np.sin(self.rpolygon.radius*2.5), 0.5,
                               np.cos(self.rpolygon.radius*2), 1.0)
        self.update()

    def on_mouse_press(self, event):
        self.rpolygon.radius = 0.2
        self.rpolygon.sides = 4
        self.rpolygon.color = 'red'
        self.update()

    def on_draw(self, ev):
        gloo.set_clear_color(color='black')
        gloo.clear()
        gloo.set_viewport(0, 0, *self.size)
        self.rpolygon.draw()
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
