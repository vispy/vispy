# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Triple viewbox, 1 spanning the other 2
=============================

Demonstrate a viewbox with col_span being 2 to span the other 2 viewboxes taking into account spacing.
"""
import sys
import numpy as np

from vispy import app
from vispy import scene


# Create canvas
canvas = scene.SceneCanvas(size=(800, 600), show=True, keys='interactive')
grid = canvas.central_widget.add_grid(spacing=(50, 150))

# Create two ViewBoxes, place side-by-side
vb1 = grid.add_view(name='vb1', border_color='green', row=0, col=0, row_span=2, col_span=1)
# First ViewBox uses a 2D pan/zoom camera
vb1.camera = 'panzoom'

# Second ViewBox uses a 3D perspective camera
vb2 = grid.add_view(name='vb2', border_color='yellow', row=0, col=0)
vb2.parent = canvas.scene
vb2.camera = scene.TurntableCamera(elevation=30, azimuth=30, up='+y')
# Third ViewBox uses a 3D perspective camera
vb3 = grid.add_view(name='vb3', border_color='red', row=1, col=0)
vb3.parent = canvas.scene
vb3.camera = scene.TurntableCamera(elevation=30, azimuth=30, up='+y')


if __name__ == '__main__' and sys.flags.interactive == 0:
    print(canvas.scene.describe_tree(with_transform=True))
    app.run()