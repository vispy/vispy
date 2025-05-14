# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Single viewbox with span higher than 1 should not show spacing despite spacing being defined
"""
import sys
import numpy as np

from vispy import app
from vispy import scene


# Create canvas
canvas = scene.SceneCanvas(size=(800, 600), show=True, keys='interactive')
grid = canvas.central_widget.add_grid(spacing=(50,150))

# Create two ViewBoxes, place side-by-side
vb1 = grid.add_view(name='vb1', border_color='yellow', row=0, col=0, row_span=2, col_span=2)
# First ViewBox uses a 2D pan/zoom camera
vb1.camera = 'panzoom'

# Now add visuals to the viewboxes.

# First a plot line:
N = 1000
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

pos = np.empty((N, 2), np.float32)
pos[:, 0] = np.linspace(-1., 1., N)
pos[:, 1] = np.random.normal(0.0, 0.5, size=N)
pos[:20, 1] = -0.5  # So we can see which side is down

# make a single plot line and display in both viewboxes
line1 = scene.visuals.Line(pos=pos.copy(), color=color, method='gl',
                           antialias=False, name='line1', parent=vb1.scene)


if __name__ == '__main__' and sys.flags.interactive == 0:
    print(canvas.scene.describe_tree(with_transform=True))
    app.run()