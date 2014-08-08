# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of RegularPolygonVisual.
"""

import vispy.app
from vispy import gloo
from vispy.scene import visuals


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        self.rpolygon = visuals.RegularPolygon(pos=(600., 500., 0), radius=160,
                                               color=(1, 0, 0, 1),
                                               border_color=(1, 1, 1, 1),
                                               sides=6)
        
        vispy.scene.SceneCanvas.__init__(self, close_keys='escape')
        self.size = (800, 800)
        self.show()
        
    def on_draw(self, ev):
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        self.draw_visual(self.rpolygon)
        

if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
