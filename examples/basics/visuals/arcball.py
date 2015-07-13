# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstration of how to interact with visuals, here with simple
arcball-style control.
"""

import sys
import numpy as np

from vispy import app
from vispy.visuals import CubeVisual, transforms
from vispy.util.quaternion import Quaternion


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, 'Cube', keys='interactive',
                            size=(400, 400))

        self.cube = CubeVisual((1.0, 0.5, 0.25), color='red',
                               edge_color='black')
        self.cube.transform = transforms.MatrixTransform()
        self.cube.transform.scale((100, 100, 0.001))
        self.cube.transform.translate((200, 200))

        self.quaternion = Quaternion()
        self.show()

    def on_resize(self, event):
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        self.cube.transforms.configure(canvas=self, viewport=vp)

    def on_draw(self, event):
        self.context.clear('white')
        self.cube.draw()

    def on_mouse_move(self, event):
        if event.button == 1 and event.last_event is not None:
            x0, y0 = event.last_event.pos
            x1, y1 = event.pos
            w, h = self.size
            self.quaternion = (self.quaternion *
                               Quaternion(*_arcball(x0, y0, w, h)) *
                               Quaternion(*_arcball(x1, y1, w, h)))
            self.cube.transform.matrix = self.quaternion.get_matrix()
            self.cube.transform.scale((100, 100, 0.001))
            self.cube.transform.translate((200, 200))
            self.update()


def _arcball(x, y, w, h):
    """Convert x,y coordinates to w,x,y,z Quaternion parameters

    Adapted from:

    linalg library

    Copyright (c) 2010-2015, Renaud Blanch <rndblnch at gmail dot com>
    Licence at your convenience:
    GPLv3 or higher <http://www.gnu.org/licenses/gpl.html>
    BSD new <http://opensource.org/licenses/BSD-3-Clause>
    """
    r = (w + h) / 2.
    x, y = -(2. * x - w) / r, -(2. * y - h) / r
    h = np.sqrt(x*x + y*y)
    return (0., x/h, y/h, 0.) if h > 1. else (0., x, y, np.sqrt(1. - h*h))

if __name__ == '__main__':
    win = Canvas()
    win.show()
    if sys.flags.interactive != 1:
        win.app.run()
