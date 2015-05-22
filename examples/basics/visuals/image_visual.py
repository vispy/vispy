# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of ImageVisual.
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

        self.image = visuals.ImageVisual(image, method='subdivide')
        self.image_transform = STTransform(scale=(7, 7), translate=(50, 50))

        # Create a TransformSystem that will tell the visual how to draw
        self.tr_sys = TransformSystem(self)
        self.tr_sys.visual_to_document = self.image_transform

        self.show()

    def on_draw(self, ev):
        gloo.clear(color='black', depth=True)
        gloo.set_viewport(0, 0, *self.physical_size)
        self.image.draw(self.tr_sys)


if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
