# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of ImageVisual.
"""

import numpy as np
import vispy.app
from vispy.gloo import gl
from vispy.scene import visuals
from vispy.scene.transforms import STTransform

image = np.random.normal(size=(100, 100, 3), loc=128,
                         scale=50).astype(np.ubyte)


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        self.image = visuals.Image(image)
        #self.image.transform = STTransform(scale=(0.01, 0.01),
                                           #translate=(-0.5, -0.5))
        vispy.scene.SceneCanvas.__init__(self, close_keys='escape')
        self.size = (800, 800)
        self.show()

    def on_draw(self, ev):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.push_viewport((0, 0) + self.size)
        #gl.glViewport(0, 0, *self.size)
        self.image.draw(self)


if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
