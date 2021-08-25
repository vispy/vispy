# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 10:200:5
"""
Rendering Markers in 3D with perspective
================================
"""

import sys

import numpy as np

from vispy import app, scene

# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view()

# # Create the markers visual
markers_data = np.array([[100, 110, 97], [100, 200, 200], [100, 333, 111]])
markers = scene.visuals.Markers(pos=markers_data, size=5, symbol='disc', parent=view.scene, scaling=True)

# create a volume visual
volume_data = np.zeros((100, 100, 100))
volume_data[95:99, 95:99, 95:99] = 1

volume = scene.visuals.Volume(volume_data, parent=view.scene)

# Create a camera
cam = scene.cameras.ArcballCamera(
    parent=view.scene, fov=0
)
cam.scale_factor = 100
view.camera = cam

# Implement key presses
@canvas.events.key_press.connect
def on_key_press(event):
    if event.text == 'p':
        if cam.fov == 0:
            cam.fov = 60
        else:
            cam.fov = 0
        print(cam.fov)


if __name__ == '__main__':
    print(__doc__)
    app.run()
