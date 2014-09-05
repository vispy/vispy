# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstration of Cube
"""

import sys

from vispy import gloo
from vispy.app import Timer
from vispy.scene import visuals, transforms, SceneCanvas


class Canvas(SceneCanvas):
    def __init__(self):
        self.cube = visuals.Cube((1.0, 0.5, 0.25), color='red',
                                 edge_color='black')
        self.theta = 0
        self.phi = 0

        SceneCanvas.__init__(self, 'Cube', keys='interactive',
                             size=(400, 400))
        self.cube.transform = transforms.AffineTransform()
        self._timer = Timer('auto', connect=self.on_timer, start=True)

    def on_draw(self, event):
        gloo.clear('white')
        self.draw_visual(self.cube, event)

    def on_timer(self, event):
        self.theta += .5
        self.phi += .5
        self.cube.transform.reset()
        self.cube.transform.rotate(self.theta, (0, 0, 1))
        self.cube.transform.rotate(self.phi, (0, 1, 0))
        self.cube.transform.scale((100, 100, 0.001))
        self.cube.transform.translate((200, 200))
        self.update()

if __name__ == '__main__':
    win = Canvas()
    win.show()
    if sys.flags.interactive != 1:
        win.app.run()
