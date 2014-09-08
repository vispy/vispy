# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstration of Polygon and subclasses
"""

import sys
import numpy as np

from vispy import gloo
from vispy.scene import visuals, transforms, SceneCanvas

# vertex positions of polygon data to draw
pos = np.array([[0, 0, 0],
               [0.25, 0.22, 0],
               [0.25, 0.5, 0],
               [0, 0.5, 0],
               [-0.25, 0.25, 0]])

pos = np.array([[0, 0],
                [10, 0],
                [10, 10],
                [20, 10],
                [20, 20],
                [25, 20],
                [25, 25],
                [20, 25],
                [20, 20],
                [10, 17],
                [5, 25],
                [9, 30],
                [6, 15],
                [15, 12.5],
                [0, 5]])

theta = np.linspace(0, 2*np.pi, 11)
pos = np.hstack([np.cos(theta)[:, np.newaxis],
                 np.sin(theta)[:, np.newaxis]])
pos[::2] *= 0.4
pos[-1] = pos[0]


class Canvas(SceneCanvas):
    def __init__(self):
        global pos
        self.visuals = []
        polygon = visuals.Polygon(pos=pos, color=(0.8, .2, 0, 1),
                                  border_color=(1, 1, 1, 1))
        polygon.transform = transforms.STTransform(scale=(200, 200),
                                                   translate=(600, 600))
        self.visuals.append(polygon)

        ellipse = visuals.Ellipse(pos=(0, 0, 0), radius=(100, 150),
                                  color=(0.2, 0.2, 0.8, 1),
                                  border_color=(1, 1, 1, 1),
                                  start_angle=180., span_angle=150.)
        ellipse.transform = transforms.STTransform(scale=(0.9, 1.5),
                                                   translate=(200, 300))
        self.visuals.append(ellipse)

        rect = visuals.Rectangle(pos=(600, 200, 0), height=200.,
                                 width=300.,
                                 radius=[30., 30., 0., 0.],
                                 color=(0.5, 0.5, 0.2, 1),
                                 border_color='white')
        self.visuals.append(rect)

        rpolygon = visuals.RegularPolygon(pos=(200., 600., 0), radius=160,
                                          color=(0.2, 0.8, 0.2, 1),
                                          border_color=(1, 1, 1, 1),
                                          sides=6)
        self.visuals.append(rpolygon)

        SceneCanvas.__init__(self, keys='interactive')
        self.size = (800, 800)
        self.show()

    def on_draw(self, ev):
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        for vis in self.visuals:
            self.draw_visual(vis)


if __name__ == '__main__':
    win = Canvas() 
    if sys.flags.interactive != 1:
        win.app.run()
