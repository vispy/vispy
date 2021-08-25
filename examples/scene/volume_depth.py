# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 10:200:5
"""
Render volumes with depth_test
================================

Controls:
* p  - toggle camera fov (perspective) between 0 and 60
"""

import sys

import numpy as np

from vispy import app, scene
from vispy.color import get_colormap
from vispy.visuals.transforms import STTransform


# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create the volume visual
im_data = np.zeros((30, 30, 30))
im_data[5:25, 5:25, 5:25] = 1
blue_cmap = get_colormap('blues')
volume_1 = scene.visuals.Volume(
    im_data,
    cmap=blue_cmap,
    parent=view.scene,
    threshold=0.5,
    method='iso'
)
volume_1.transform = scene.STTransform(translate=(0, -10, -10))

vertices = np.array(
    [
        [0, 0, 0],
        [0, 10, 0],
        [0, 10, 10],
        [0, 0, 10],
        [50, 5, 5]
    ]
)
faces = np.array(
    [
        [0, 1, 2],
        [0, 2, 3],
        [0, 1, 4],
        [1, 2, 4],
        [2, 3, 4],
        [3, 0, 4]
    ]
)
mesh = scene.visuals.Mesh(vertices, faces, color=(.5, .7, .5, 1), parent=view.scene)

# Create and set the camera
fov = 60
cam = scene.cameras.ArcballCamera(
    parent=view.scene,
    fov=fov,
    name='Arcball'
)
view.camera = cam


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