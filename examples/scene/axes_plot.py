# -*- coding: utf-8 -*-
# vispy: gallery 2
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Simple Line with Axis 
=====================

"""
import sys
import numpy as np

from vispy import scene, app

canvas = scene.SceneCanvas(keys='interactive', size=(600, 600), show=True)
grid = canvas.central_widget.add_grid(margin=10)
grid.spacing = 0

title = scene.Label("Plot Title", color='white')
title.height_max = 40
grid.add_widget(title, row=0, col=0, col_span=2)

yaxis = scene.AxisWidget(orientation='left',
                         axis_label='Y Axis',
                         axis_font_size=12,
                         axis_label_margin=50,
                         tick_label_margin=5)
yaxis.width_max = 80
grid.add_widget(yaxis, row=1, col=0)

xaxis = scene.AxisWidget(orientation='bottom',
                         axis_label='X Axis',
                         axis_font_size=12,
                         axis_label_margin=50,
                         tick_label_margin=5)

xaxis.height_max = 80
grid.add_widget(xaxis, row=2, col=1)

right_padding = grid.add_widget(row=1, col=2, row_span=1)
right_padding.width_max = 50

view = grid.add_view(row=1, col=1, border_color='white')
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
