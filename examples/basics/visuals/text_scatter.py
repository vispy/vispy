# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Demonstration of ability to scatter text parts and assign different colors.
"""

import sys
from vispy import app, gloo, visuals
import numpy as np


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, keys='interactive',
                            size=(800, 800))

        self.n_iterations = 0

        self.text_parts = [
            'This',
            'is',
            'a',
            'multicolored',
            'scattered',
            'text']

        self.x = 100 + np.arange(len(self.text_parts))*100
        self.y = 400 + (np.sin(2 * np.pi * (self.x/self.x[-1]))*100)

        self.text_positions = np.c_[self.x, self.y]

        color = np.ones((len(self.text_parts), 4), dtype=np.float32)
        color[:, 0] = np.linspace(0, 1, len(self.text_parts))
        color[:, 1] = color[::-1, 0]

        self.colors = color

        self.text = visuals.TextVisual(self.text_parts, bold=True,
                                       pos=self.text_positions,
                                       color=self.colors)

    def on_draw(self, event):
        gloo.clear(color='white')
        gloo.set_viewport(0, 0, *self.physical_size)
        self.text.draw()

    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        self.text.transforms.configure(canvas=self, viewport=vp)


if __name__ == '__main__':
    c = Canvas()
    c.show()

    def update(ev):
        x = c.text.pos[:, 0]
        y = 400 + (np.sin(2 * np.pi * ((x/x[-1]))+(c.n_iterations/5))*100)

        color = np.ones((len(c.text_parts), 4), dtype=np.float32)
        color[:, 0] = np.linspace(0, 1, len(c.text_parts))
        color[:, 1] = color[::-1, 0]
        color = np.roll(color, c.n_iterations // len(color), axis=0)
        c.text.pos = np.c_[x, y]
        c.text.color = color
        c.update()
        c.n_iterations += 1

    timer = app.Timer()
    timer.connect(update)
    timer.start(0.1)

    if sys.flags.interactive != 1:
        app.run()
