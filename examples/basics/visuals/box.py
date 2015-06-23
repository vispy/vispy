# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of Mesh visual.
"""

import numpy as np
from vispy import app, gloo, visuals
from vispy.geometry import create_box
# from vispy.visuals.transforms import STTransform
from vispy.visuals.transforms import (STTransform, AffineTransform,
                                      ChainTransform)


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=(800, 550))

        vertices, faces, outline = create_box(width=2, height=4, depth=8,
                                               width_segments=4,
                                               height_segments=8,
                                               depth_segments=16)

        self.box = visuals.BoxVisual(width=4, height=4, depth=8, width_segments=4,
                        height_segments=8, depth_segments=16,
                        vertex_colors=vertices['color'],
                        edge_color='b')


        self.rotation = AffineTransform()

        self.box.transform = ChainTransform([STTransform(translate=(400, 400),
                                                    scale=(40, 40, 1)),
                                        self.rotation])
          
        self.show()

        self.timer = app.Timer(connect=self.rotate)
        self.timer.start(0.016)

    def rotate(self, event):
        # rotate with an irrational amount over each axis so there is no
        # periodicity
        self.rotation.rotate(0.6, (2 ** 0.5, 3 ** 0.5, 7 ** 0.5))
        self.update()

    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)

        self.box.transforms.configure(canvas=self, viewport=vp)

    def on_draw(self, ev):
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        gloo.set_viewport(0, 0, *self.physical_size)
        gloo.clear(color='white', depth=True)
        
        self.box.draw()


if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        app.run()
