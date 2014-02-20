# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of ImageVisual. 
"""

import numpy as np
import vispy.app
from vispy.gloo import gl
from vispy.visuals.all import ImageVisual
from vispy.visuals.transforms import STTransform

image = np.random.normal(size=(100, 100, 3), loc=128, scale=50).astype(np.ubyte)


class Canvas(vispy.app.Canvas):
    def __init__(self):
        self.image = ImageVisual(image)
        self.image.transform = STTransform(scale=(0.01, 0.01), translate=(-0.5, -0.5))
        vispy.app.Canvas.__init__(self)
        self.size = (800, 800)
        self.show()
        
    def on_paint(self, ev):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glViewport(0, 0, *self.size)
        self.image.paint()
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
    


