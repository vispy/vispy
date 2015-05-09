# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstrates viewing a single visual multiple times in a single frame.


"""

import numpy as np
import vispy.app
from vispy import gloo
from vispy import visuals
from vispy.visuals.transforms import STTransform, TransformSystem

image = np.random.normal(size=(100, 100, 3), loc=128,
                         scale=50).astype(np.ubyte)


class Canvas(vispy.app.Canvas):
    def __init__(self):
        vispy.app.Canvas.__init__(self, keys='interactive', size=(800, 800))
        
        # create an image (which is implicitly a view of itself)
        self.image = visuals.ImageVisual(image, method='subdivide')
        # and create a second view on the image
        self.views = [self.image.default_view, self.image.view()]
        
        for view in self.views:
            # Set up both views to use this canvas for document and framebuffer
            # transforms
            view.transforms.canvas = self
        
            # give each view a different transform
            # (this is shorthand for visual.transforms.visual_to_document = ...)
            view.transform = STTransform(scale=(7, 7), translate=(50, 50))

            # ..and different clipping:
            view.attach(Clipper(...))
        
        # implicitly attach a single filter to both views:
        self.image.attach(ColorFilter(...))
        
        self.show()

    def on_draw(self, ev):
        gloo.clear(color='black', depth=True)
        gloo.set_viewport(0, 0, *self.physical_size)
        for view in self.views:
            view.draw()


if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
