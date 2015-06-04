# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
This example demonstrates how to draw lines with one or more arrow heads.
"""

import sys

from vispy import app, gloo, visuals
from vispy.geometry import curves
from vispy.visuals.transforms import STTransform, NullTransform


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, title='Arrows example',
                            keys='interactive', size=(400, 750))

        line1 = curves.curve4_bezier(
            (10, 0),
            (50, -190),
            (350, 190),
            (390, 0)
        )
        arrows1 = (line1[-2:],)

        line2 = curves.curve4_bezier(
            (10, 0),
            (190, -190),
            (210, 190),
            (390, 0)
        )
        arrows2 = (
            line2[1::-1],
            line2[-2:]
        )

        line3 = curves.curve3_bezier(
            (10, 0),
            (30, 200),
            (390, 0)
        )

        print(arrows1)
        print(arrows2)

        self.lines = [
            visuals.ArrowVisual(line1, color='w', width=2, method='agg',
                                arrows=arrows1, arrow_type='curved'),
            visuals.ArrowVisual(line2, color='w', width=2, method='agg',
                                arrows=arrows2, arrow_type='curved'),
            visuals.LineVisual(line3, color='w', width=2, method='agg')
        ]

        # Translate each line visual downwards
        for i, line in enumerate(self.lines):
            x = 0
            y = 200 * (i + 1)

            line.transform = STTransform(translate=[x, y])

        self.texts = [
            visuals.TextVisual('4 point Bezier curve', bold=True, color='w',
                               font_size=24, pos=(200, 75)),
            visuals.TextVisual('3 point Bezier curve', bold=True, color='w',
                               font_size=24, pos=(200, 525)),
        ]

        for text in self.texts:
            text.transform = NullTransform()

        # Initialize transform systems for each visual
        self.visuals = self.lines + self.texts
        for visual in self.visuals:
            visual.tr_sys = visuals.transforms.TransformSystem(self)
            visual.tr_sys.visual_to_document = visual.transform

        self.show()

    def on_draw(self, event):
        gloo.clear('black')
        gloo.set_viewport(0, 0, *self.physical_size)

        for visual in self.visuals:
            visual.draw(visual.tr_sys)

if __name__ == '__main__':
    win = Canvas()

    if sys.flags.interactive != 1:
        app.run()
