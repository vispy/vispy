# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstration of Polygon and subclasses
"""

#import numpy as np

import sys
from vispy import app, gloo, visuals
from vispy.visuals import colorbar

class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=(800, 800))

        self.colorbar = colorbar.ColorbarVisual(colormap="linear", clim=("top", "bottom"))
        self.show()

    def on_draw(self, ev):
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.set_viewport(0, 0, *self.physical_size)
        gloo.clear()

        # for vis in self.visuals:
        #    vis.draw(vis.tr_sys)


if __name__ == '__main__':
    win = Canvas() 
    if sys.flags.interactive != 1:
        win.app.run()
