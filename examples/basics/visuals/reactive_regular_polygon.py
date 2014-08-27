# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of reactive RegularPolygonVisual. 
"""

import vispy
from vispy import gloo, app
from vispy.scene import visuals
import numpy as np


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        self.rpolygon = visuals.RegularPolygon(pos=(400.0, 400.0, 0), 
                                               radius=80.,
                                               color=(1, 0, 0, 1),
                                               border_color=(1, 1, 1, 1),
                                               sides=4)
        
        vispy.scene.SceneCanvas.__init__(self, keys='interactive')
        self.size = (800, 800)
        self.show()
        
        self.rfactor = 0.01
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)

    def on_timer(self, event):
        if (self.rpolygon.radius > 400. or self.rpolygon.radius < 80.):
            self.rfactor *= -1
        self.rpolygon.radius += self.rfactor
        self.rpolygon.sides += 100 * self.rfactor
        self.rpolygon.color = (np.sin(self.rpolygon.radius * 0.00625), 0.5,
                               np.cos(self.rpolygon.radius * 0.005), 1.0)
        self.update()

    def on_mouse_press(self, event):
        self.rpolygon.radius = 80.
        self.rpolygon.sides = 4
        self.rpolygon.color = 'red'
        self.update()

    def on_draw(self, ev):
        gloo.clear(color='black')
        gloo.set_viewport(0, 0, *self.size)
        self.draw_visual(self.rpolygon)
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
