# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Test automatic layout of multiple viewboxes using Grid.
"""
import sys
import numpy as np

from vispy import scene, app

canvas = scene.SceneCanvas(keys='interactive', size=(600, 600), show=True)
grid = canvas.central_widget.add_grid(margin=10)
grid.spacing = 0

title = scene.Label("Plot Title", color='white')
title.stretch = (1, 0.1)
grid.add_widget(title, row=0, col=2)

yaxis = scene.AxisWidget(orientation='left')
yaxis.stretch = (0.2, 1)
grid.add_widget(yaxis, row=1, col=1)

ylabel = scene.Label('Y Axis', rotation=-90, color='white')
ylabel.stretch = (0.1, 1)
grid.add_widget(ylabel, row=1, col=0)

xaxis = scene.AxisWidget(orientation='bottom')
grid.add_widget(xaxis, row=2, col=2)
xaxis.stretch = (1, 0.1)

xlabel = scene.Label('X Axis', color='white')
xlabel.stretch = (1, 0.1)
grid.add_widget(xlabel, row=3, col=2)

view = grid.add_view(row=1, col=2, border_color='white')
data = np.random.normal(size=(1000, 2))
data[0] = -10, -10
data[1] = 10, -10
data[2] = 10, 10
data[3] = -10, 10
data[4] = -10, -10
plot = scene.Line(data, parent=view.scene)
view.camera = 'panzoom'

xaxis.link_view(view)
yaxis.link_view(view)


if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
