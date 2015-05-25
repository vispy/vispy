# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstration of Cube
"""

import sys

from vispy import app, gloo
from vispy.visuals import CubeVisual, transforms


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, 'Cube', keys='interactive',
                            size=(400, 400))

        self.cube = CubeVisual((1.0, 0.5, 0.25), color='red',
                               edge_color='black')
        self.theta = 0
        self.phi = 0

        # Create a TransformSystem that will tell the visual how to draw
        self.cube_transform = transforms.AffineTransform()
        self.tr_sys = transforms.TransformSystem(self)
        self.tr_sys.visual_to_document = self.cube_transform

        self._timer = app.Timer('auto', connect=self.on_timer, start=True)

        self.show()

    def on_draw(self, event):
        gloo.set_viewport(0, 0, *self.physical_size)
        gloo.clear('white')
        self.tr_sys.auto_configure()
        self.cube.draw(self.tr_sys)

    def on_timer(self, event):
        self.theta += .5
        self.phi += .5
        self.cube_transform.reset()
        self.cube_transform.rotate(self.theta, (0, 0, 1))
        self.cube_transform.rotate(self.phi, (0, 1, 0))
        self.cube_transform.scale((100, 100, 0.001))
        self.cube_transform.translate((200, 200))
        self.update()

if __name__ == '__main__':
    win = Canvas()
    win.show()
    if sys.flags.interactive != 1:
        win.app.run()
