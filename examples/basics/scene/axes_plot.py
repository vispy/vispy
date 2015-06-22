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
grid = canvas.central_widget.add_grid()
grid.spacing = 0

axis = scene.AxisWidget()
grid.add_widget(axis, row=0, col=0)

view = grid.add_view(row=0, col=1)
plot = scene.Line(np.random.normal(size=(1000,2)), parent=view.scene)
view.camera = 'panzoom'

axis.link_view(view)


if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
