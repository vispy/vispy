#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
This example demonstrates how to visualise a NetworkX graph using the
GraphVisual.
"""

import sys

import numpy as np
import networkx as nx

from vispy import app, gloo, visuals
from vispy.visuals.graphs import layouts
from vispy.visuals.transforms import STTransform


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, title="Simple NetworkX Graph",
                            keys="interactive", size=(600, 600))

        self.graph = nx.fast_gnp_random_graph(1000, 0.0006, directed=True)

        self.visual = visuals.GraphVisual(
            # np.asarray(nx.to_numpy_matrix(self.graph)),
            nx.adjacency_matrix(self.graph),
            layout=layouts.get_layout('force_directed'),
            line_color=(1.0, 1.0, 1.0, 1.0),
            arrow_type="stealth",
            arrow_size=15,
            node_symbol="disc",
            node_size=10,
            face_color="red",
            border_width=0.0,
            animate=True,
            directed=True
        )

        self.visual.events.update.connect(lambda evt: self.update())
        self.visual.transform = STTransform(self.visual_size, (20, 20))

        self.timer = app.Timer(interval=0, connect=self.animate, start=True)

        self.show()

    @property
    def visual_size(self):
        return (
            self.physical_size[0] - 40,
            self.physical_size[1] - 40
        )

    def on_resize(self, event):
        self.visual.transform.scale = self.visual_size

        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        self.visual.transforms.configure(canvas=self, viewport=vp)

    def on_draw(self, event):
        gloo.clear('black')
        self.visual.draw()

    def animate(self, event):
        ready = self.visual.animate_layout()

        if ready:
            self.timer.disconnect(self.animate)


if __name__ == '__main__':
    win = Canvas()

    if sys.flags.interactive != 1:
        app.run()
