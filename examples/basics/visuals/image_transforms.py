# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# vispy: gallery 2

"""
Simple demonstration of ImageVisual.
"""

import numpy as np
import vispy.app
from vispy import gloo
from vispy.scene import visuals
from vispy.scene.transforms import (AffineTransform, STTransform, arg_to_array,
                                    LogTransform, PolarTransform, 
                                    BaseTransform)

image = np.random.normal(size=(100, 100, 3))
image[20:80, 20:80] += 3.
image[50] += 3.
image[:, 50] += 3.

image = ((image-image.min()) *
         (253. / (image.max()-image.min()))).astype(np.ubyte)


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        self.images = [visuals.Image(image, method='impostor')
                       for i in range(4)]
        self.images[0].transform = (STTransform(scale=(30, 30),
                                                translate=(600, 600)) * 
                                    SineTransform() *
                                    STTransform(scale=(0.1, 0.1),
                                                translate=(-5, -5)))

        tr = AffineTransform()
        tr.rotate(30, (0, 0, 1))
        tr.scale((3, 3))
        self.images[1].transform = (STTransform(translate=(200, 600)) *
                                    tr *
                                    STTransform(translate=(-50, -50)))

        self.images[2].transform = (STTransform(scale=(3, -150),
                                                translate=(200, 100)) *
                                    LogTransform((0, 2, 0)) *
                                    STTransform(scale=(1, -0.01),
                                                translate=(-50, 1.3)))

        self.images[3].transform = (STTransform(scale=(400, 400),
                                                translate=(600, 300)) *
                                    PolarTransform() *
                                    STTransform(scale=(np.pi/200, 0.005),
                                                translate=(-3*np.pi/4., 0.1)))

        vispy.scene.SceneCanvas.__init__(self, keys='interactive')
        self.size = (800, 800)
        self.show()

    def on_draw(self, ev):
        gloo.clear(color='black', depth=True)
        self.push_viewport((0, 0) + self.size)
        for img in self.images:
            self.draw_visual(img)


# A simple custom Transform
class SineTransform(BaseTransform):
    """
    Add sine wave to y-value for wavy effect.
    """
    glsl_map = """
        vec4 sineTransform(vec4 pos) {
            return vec4(pos.x, pos.y + sin(pos.x), pos.z, 1);
        }"""

    glsl_imap = """
        vec4 sineTransform(vec4 pos) {
            return vec4(pos.x, pos.y - sin(pos.x), pos.z, 1);
        }"""

    Linear = False

    @arg_to_array
    def map(self, coords):
        ret = coords.copy()
        ret[..., 1] += np.sin(ret[..., 0])
        return ret

    @arg_to_array
    def imap(self, coords):
        ret = coords.copy()
        ret[..., 1] -= np.sin(ret[..., 0])
        return ret

    def inverse(self):
        return InvSineTransform()


class InvSineTransform(BaseTransform):
    glsl_map = SineTransform.glsl_imap
    glsl_imap = SineTransform.glsl_map

    Linear = False

    map = SineTransform.imap
    imap = SineTransform.map

    def inverse(self):
        return SineTransform()

if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
