# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import sys

from vispy import app, scene, io

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()

# Create two ViewBoxes, place side-by-side
vb1 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)
vb2 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)
vb3 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)
vb4 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)
vb1.clip_method = 'fragment'
vb2.clip_method = 'viewport'
vb3.clip_method = 'viewport'
vb4.clip_method = 'fbo'
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
for vb in (vb1, vb2, vb3, vb4):
    vb.camera = scene.TurntableCamera()
    vb.camera.fov = 50

if __name__ == '__main__':
    if sys.flags.interactive != 1:
        app.run()
