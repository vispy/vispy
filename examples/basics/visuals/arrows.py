#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
This example demonstrates how to draw lines with one or more arrow heads.
"""

import sys

import numpy as np
from vispy import app, gloo, visuals
from vispy.geometry import curves
from vispy.visuals.transforms import STTransform


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, title='Arrows example',
                            keys='interactive', size=(1050, 650))

        line1 = curves.curve4_bezier(
            (10.0, 0.0),
            (50, -190),
            (350, 190),
            (390, 0.0)
        )
        arrows1 = np.array([
            line1[-2],
            line1[-1]
        ]).reshape((1, 4))

        line2 = curves.curve4_bezier(
            (10.0, 0.0),
            (190, -190),
            (210, 190),
            (390, 0.0)
        )
        arrows2 = np.array([
            line2[1],
            line2[0],
            line2[-2],
            line2[-1]
        ]).reshape((2, 4))

        line3 = curves.curve3_bezier(
            (10.0, 0.0),
            (50, 190),
            (390, 0.0)
        )

        arrows3 = np.array([
            line3[-2],
            line3[-1]
        ]).reshape((1, 4))

        arrow_types = ["curved", "stealth", "inhibitor_round", "angle_60"]
        self.lines = []

        for i, arrow_type in enumerate(arrow_types):
            arrows = [
                visuals.ArrowVisual(line1, color='w', width=6, method='agg',
                                    arrows=arrows1, arrow_type=arrow_type,
                                    arrow_size=30.0),
                visuals.ArrowVisual(line2, color='w', width=2, method='agg',
                                    arrows=arrows2, arrow_type=arrow_type,
                                    arrow_size=5.0),
                visuals.ArrowVisual(line3, color='w', width=4, method='agg',
                                    arrows=arrows3, arrow_type=arrow_type,
                                    arrow_size=10.0)
            ]

            # Translate each line visual downwards
            for j, visual in enumerate(arrows):
                x = 50 + (i * 250)
                y = 100 + (200 * j)

                visual.transform = STTransform(translate=[x, y],
                                               scale=(0.5, 1.0))
                visual.events.update.connect(lambda event: self.update())

            self.lines.extend(arrows)

        self.show()

    def on_draw(self, event):
        gloo.clear('black')

        for visual in self.lines:
            visual.draw()

    def on_resize(self, event):
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        for visual in self.lines:
            visual.transforms.configure(canvas=self, viewport=vp)

if __name__ == '__main__':
    win = Canvas()

    if sys.flags.interactive != 1:
        app.run()
