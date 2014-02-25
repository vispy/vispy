# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of ImageVisual. 
"""

import numpy as np
import vispy.app
from vispy.gloo import gl
from vispy.visuals import ImageVisual
from vispy.visuals.transforms import *

image = np.random.normal(size=(100, 100, 3))
image[20:80, 20:80] += 10.
image = ((image-image.min()) * (255. / image.max())).astype(np.ubyte)

class Canvas(vispy.app.Canvas):
    def __init__(self):
        self.images = [ImageVisual(image) for i in range(4)]
        base = STTransform(scale=(0.009, 0.009), translate=(-0.45, -0.45))
        self.images[0].transform = (STTransform(translate=(-0.5, -0.5)) * 
                                    base)
        
        tr = AffineTransform()
        tr.rotate(30, (0,0,1))
        tr.scale((0.7, 0.7))
        self.images[1].transform = (STTransform(translate=(0.5, -0.5)) *
                                    tr * 
                                    base)
        
        self.images[2].transform = (STTransform(scale=(1, 0.14),
                                                translate=(-0.5, 0)) * 
                                    LogTransform((0, 2, 0)) *
                                    STTransform(scale=(0.009, 1),
                                                translate=(-0.45, 1)))
        
        self.images[3].transform = (STTransform(scale=(1, 1),
                                                translate=(0.5, 0.2)) * 
                                    PolarTransform() *
                                    STTransform(scale=(np.pi/200, 0.005),
                                                translate=(np.pi/4., 0.1)))
        
        vispy.app.Canvas.__init__(self)
        self.size = (800, 800)
        self.show()
        
    def on_paint(self, ev):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glViewport(0, 0, *self.size)
        for img in self.images:
            img.paint()
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
    


