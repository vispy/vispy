#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
This example demonstrates how to visualise a NetworkX graph using the
GraphVisual.
"""

import sys

import networkx as nx
import numpy as np

from vispy import app, gloo, visuals
from vispy.visuals.transforms import STTransform


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, title="Simple NetworkX Graph",
                            keys="interactive", size=(800, 600))

        self.graph = nx.fast_gnp_random_graph(100, 0.02)

        self.visual = visuals.GraphVisual(
            nx.adjacency_matrix(self.graph),
            line_color=(1.0, 1.0, 1.0, 1.0),
            arrow_type="stealth",
            arrow_size=7.5,
            node_symbol="disc",
            node_size=10,
            face_color="red",
            edge_width=0.0
        )

        self.visual.events.update.connect(lambda evt: self.update())
        self.visual.transform = STTransform(self.physical_size)

        self.show()

    def on_resize(self, event):
        self.visual.transform.scale = self.physical_size

        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        self.visual.transforms.configure(canvas=self, viewport=vp)

    def on_draw(self, event):
        gloo.clear('black')
        self.visual.draw()


if __name__ == '__main__':
    win = Canvas()

    if sys.flags.interactive != 1:
        app.run()
