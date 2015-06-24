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
from vispy.visuals.transforms import STTransform

image = np.random.normal(size=(100, 100, 3), loc=128,
                         scale=50).astype(np.ubyte)


class Canvas(vispy.app.Canvas):
    def __init__(self):
        vispy.app.Canvas.__init__(self, keys='interactive', size=(800, 800))
        self.image = visuals.ImageVisual(image, method='subdivide')
        self.image.transform = STTransform(scale=(7, 7), translate=(50, 50))
        self.show()

    def on_draw(self, ev):
        gloo.clear(color='black', depth=True)
        self.image.draw()

    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        self.image.transforms.configure(canvas=self, viewport=vp)


if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
