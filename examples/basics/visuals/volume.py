# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstration of Volume
"""

import sys

from vispy import gloo
from vispy.app import Timer
from vispy.scene import visuals, transforms, SceneCanvas

class Canvas(SceneCanvas):
    def __init__(self):
        self.volume = visuals.Volume()
        self.theta = 30
        self.phi = 30

        SceneCanvas.__init__(self, 'Volume', keys='interactive',
                             size=(400, 400))
        self.volume.transform = transforms.AffineTransform()
        self._timer = Timer('auto', connect=self.on_timer, start=True)

    def on_timer(self, event):
        self.theta += 0.5 * 0
        self.phi += 0.5 * 0
        self.volume.transform.reset()
        self.volume.transform.rotate(self.theta, (0, 0, 1))
        self.volume.transform.rotate(self.phi, (0, 1, 0))
        self.volume.transform.scale((100, 100, 0.001))
        self.volume.transform.translate((200, 200))
        self.update()

    def on_draw(self, event):
        gloo.clear('white')
        self.draw_visual(self.volume, event)


if __name__ == '__main__':
    win = Canvas()
    win.show()
    if sys.flags.interactive != 1:
        win.app.run()
