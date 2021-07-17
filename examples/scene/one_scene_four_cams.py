# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2

"""
Single Scene in Multiple View boxes
===================================

Demonstrating a single scene that is shown in four different viewboxes,
each with a different camera.

Note:
    This example just creates four scenes using the same visual.
    Multiple views are currently not available. See #1124 how this could
    be achieved.
"""

import sys

from vispy import app, scene, io

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()

# Create four ViewBoxes
vb1 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)
vb2 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)
vb3 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)
vb4 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)
scenes = vb1.scene, vb2.scene, vb3.scene, vb4.scene

# Put viewboxes in a grid
grid = canvas.central_widget.add_grid()
grid.padding = 6
grid.add_widget(vb1, 0, 0)
grid.add_widget(vb2, 0, 1)
grid.add_widget(vb3, 1, 0)
grid.add_widget(vb4, 1, 1)

# Create some visuals to show
im1 = io.load_crate().astype('float32') / 255
for par in scenes:
    image = scene.visuals.Image(im1, grid=(20, 20), parent=par)

# Assign cameras
vb1.camera = scene.BaseCamera()
vb2.camera = scene.PanZoomCamera()
vb3.camera = scene.TurntableCamera()
vb4.camera = scene.FlyCamera()

if __name__ == '__main__':
    if sys.flags.interactive != 1:
        app.run()
