# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2

"""
Demonstrating two scenes that share the same camera view by linking the
cameras.
"""

import numpy as np

from vispy import app, scene, io

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()

# Create two ViewBoxes, place side-by-side
vb1 = scene.widgets.ViewBox(border_color='yellow', parent=canvas.scene)
vb2 = scene.widgets.ViewBox(border_color='blue', parent=canvas.scene)
#
grid = canvas.central_widget.add_grid()
grid.padding = 6
grid.add_widget(vb1, 0, 0)
grid.add_widget(vb2, 0, 1)

# Create the image
im1 = io.load_crate().astype('float32') / 255
# Make gray, smooth, and take derivatives: edge enhancement
im2 = im1[:, :, 1]
im2 = (im2[1:-1, 1:-1] + im2[0:-2, 1:-1] + im2[2:, 1:-1] + 
       im2[1:-1, 0:-2] + im2[1:-1, 2:]) / 5
im2 = 0.5 + (np.abs(im2[0:-2, 1:-1] - im2[1:-1, 1:-1]) + 
             np.abs(im2[1:-1, 0:-2] - im2[1:-1, 1:-1]))

image1 = scene.visuals.Image(im1, parent=vb1.scene)
image2 = scene.visuals.Image(im2, parent=vb2.scene)

# Set 2D camera (PanZoomCamera, TurnTableCamera)
vb1.camera, vb2.camera = scene.PanZoomCamera(), scene.PanZoomCamera()
vb1.camera.aspect = vb2.camera.aspect = 1  # no auto-scale
vb1.camera.link(vb2.camera)

# Set the view bounds to show the entire image with some padding
vb1.camera.set_range()


if __name__ == '__main__':
    app.run()
