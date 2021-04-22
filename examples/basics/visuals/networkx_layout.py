# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
from vispy import scene
from vispy.visuals.graphs import layouts
import networkx as nx
g = nx.erdos_renyi_graph(100, .2)
layout = layouts.get_layout("networkx_layout", graph=g, layout="spring")

# create canvas
canvas = scene.SceneCanvas(title='Simple NetworkX Graph', size=(
    600, 600), bgcolor='black', show=True)
view = canvas.central_widget.add_view('panzoom')
visual = scene.visuals.Graph(
    layout.adj, layout=layout, line_color=(1, 1, 1, .5), arrow_type="stealth",
    arrow_size=30, node_symbol="disc", node_size=20,
    face_color=(1, 0, 0, 1), border_width=0.0, animate=False, directed=False,
    parent=view.scene)


@canvas.events.draw.connect
def on_draw(event):
    if not visual.animate_layout():
        canvas.update()


canvas.show()
