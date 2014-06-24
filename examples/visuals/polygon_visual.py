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


class Canvas(vispy.app.Canvas):
    def __init__(self):
        self.polygon = visuals.Polygon(pos=pos, color=(1, 0, 0, 1),
                                       border_color=(1, 1, 1, 1))
        
        vispy.app.Canvas.__init__(self)
        self.size = (800, 800)
        self.show()
        
    def on_draw(self, ev):
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *self.size)
        self.polygon.paint()
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
