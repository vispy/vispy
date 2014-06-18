# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Per Rosengren
# Date:   19/03/2014
# -----------------------------------------------------------------------------
"""
Take a screenshot and save it.
"""

import logging

import vispy.gloo.util
import vispy.util.dataio

logger = logging.getLogger(__name__)


class Screenshot(object):

    def __init__(self, canvas):
        self.canvas = canvas
        self.image = None
        self.canvas_on_draw = self.canvas.on_draw
        self.canvas.on_draw = self.on_draw

    def on_draw(self, event):
        self.canvas_on_draw(event)
        self.image = vispy.gloo.util._screenshot(
            (0, 0, self.canvas.size[0], self.canvas.size[1]))[::-1]
        self.canvas.on_draw = self.canvas_on_draw

    def save(self, image_path="screenshot.png"):
        while self.image is None:
            self.canvas.app.process_events()
        vispy.util.dataio.imsave(image_path, self.image)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    import graph
    c = graph.Canvas()
    s = Screenshot(c)
    c.show()
    s.save(image_path="screenshot.png")
