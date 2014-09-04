# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstration of Cube
"""

import numpy as np
import vispy.app
from vispy import gloo
from vispy.scene import visuals, transforms

class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        self.cube = visuals.Cube()
        self.cube.transform = transforms.AffineTransform()
        self.cube.transform.scale((100, 100))
        self.cube.transform.translate((200, 200))

        self.theta = 0
        self.phi = 0

        vispy.scene.SceneCanvas.__init__(self, keys='interactive')
        self.size = (800, 800)
        self.show()

#        self._timer = vispy.app.Timer('auto', connect=self.on_timer, start=True)

    def on_draw(self, event):
        gloo.set_clear_color('white')
        gloo.clear()
        self.draw_visual(self.cube)

    def on_timer(self, event):
        self.theta += .05
        self.phi += .05
        self.cube.transform.rotate(self.theta, (0, 0, 1))
        self.cube.transform.rotate(self.phi, (0, 1, 0))
        self.update()

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()


"""
        self.cube.transform = transforms.STTransform(
            scale=(200, 200),
            translate=(200, 200))
"""

