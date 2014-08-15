# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of RectPolygonVisual. 
"""

import vispy.app
from vispy import gloo
from vispy.scene import visuals, transforms


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        self.rectpolygon = visuals.RectPolygon(pos=(400, 400, 0), radius=10,
                                           height=100., width=100., degree=0.3,
                                           color='red', border_color='white')
        
        vispy.scene.SceneCanvas.__init__(self, close_keys='escape')
        self.size = (800, 800)
        self.show()
        
    def on_draw(self, ev):
        gloo.clear('black')
        self.draw_visual(self.rectpolygon)
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
