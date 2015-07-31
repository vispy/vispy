# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
This example demonstrates how to draw curved lines (bezier).
"""

import sys

from vispy import app, gloo, visuals
from vispy.geometry import curves
from vispy.visuals.transforms import STTransform, NullTransform


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, title='Bezier lines example',
                            keys='interactive', size=(400, 750))

        self.lines = [
            visuals.LineVisual(curves.curve4_bezier(
                (10, 0),
                (50, -190),
                (350, 190),
                (390, 0)
            ), color='w', width=2, method='agg'),
            visuals.LineVisual(curves.curve4_bezier(
                (10, 0),
                (190, -190),
                (210, 190),
                (390, 0)
            ), color='w', width=2, method='agg'),
            visuals.LineVisual(curves.curve3_bezier(
                (10, 0),
                (30, 200),
                (390, 0)
            ), color='w', width=2, method='agg')
        ]

        # Translate each line visual downwards
        for i, line in enumerate(self.lines):
            x = 0
            y = 200 * (i + 1)

            line.transform = STTransform(translate=[x, y])

        self.texts = [
            visuals.TextVisual('Third order curve', bold=True, color='w',
                               font_size=14, pos=(200, 75)),
            visuals.TextVisual('Quadratic curve', bold=True, color='w',
                               font_size=14, pos=(200, 525)),
        ]

        for text in self.texts:
            text.transform = NullTransform()

        self.visuals = self.lines + self.texts
        self.show()

    def on_draw(self, event):
        gloo.clear('black')
        gloo.set_viewport(0, 0, *self.physical_size)

        for visual in self.visuals:
            visual.draw()

    def on_resize(self, event):
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        for visual in self.visuals:
            visual.transforms.configure(canvas=self, viewport=vp)


if __name__ == '__main__':
    win = Canvas()

    if sys.flags.interactive != 1:
        app.run()
