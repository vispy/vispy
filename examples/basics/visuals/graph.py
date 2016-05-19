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

from vispy import app, visuals
from vispy.visuals.graphs import layouts
from vispy.visuals.transforms import STTransform


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, title="Simple NetworkX Graph",
                            keys="interactive", size=(600, 600))

        graph = nx.adjacency_matrix(
            nx.fast_gnp_random_graph(500, 0.005, directed=True))
        layout = layouts.get_layout('force_directed', iterations=100)

        self.visual = visuals.GraphVisual(
            graph, layout=layout, line_color='black', arrow_type="stealth",
            arrow_size=30, node_symbol="disc", node_size=20,
            face_color=(1, 0, 0, 0.5), border_width=0.0, animate=True,
            directed=False)

        self.visual.transform = STTransform(self.visual_size, (20, 20))
        self.show()

    @property
    def visual_size(self):
        return self.physical_size[0] - 40, self.physical_size[1] - 40

    def on_resize(self, event):
        self.visual.transform.scale = self.visual_size
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        self.visual.transforms.configure(canvas=self, viewport=vp)

    def on_draw(self, event):
        self.context.clear('white')
        self.visual.draw()
        if not self.visual.animate_layout():
            self.update()


if __name__ == '__main__':
    win = Canvas()

    if sys.flags.interactive != 1:
        app.run()
