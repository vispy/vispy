# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 10:200:5
"""
Render volumes with depth_test
================================

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
im_data = np.zeros((50, 50, 50))
im_data[30:40, 25:35, 25:35] = 1
green_cmap = get_colormap('greens')
volume = scene.visuals.Volume(
    im_data,
    cmap=green_cmap,
    parent=view.scene,
    threshold=0.5,
    method='iso'
)

blue_cmap = get_colormap('blues')
volume_2 = scene.visuals.Volume(
    im_data,
    cmap=blue_cmap,
    parent=view.scene,
    threshold=0.5,
    method='iso'
)
volume_2.transform = scene.STTransform(translate=(30, 0, 0))

markers_data = np.array([
    [20, 30, 35],
    [45, 30, 30],
    [70, 30, 35]
])
markers = scene.visuals.Markers(pos=markers_data, size=20, parent=view.scene)

# Create and set the camera
fov = 60.
cam = scene.cameras.TurntableCamera(
    parent=view.scene,
    fov=fov,
    name='Turntable'
)
view.camera = cam

# Create an XYZAxis visual
axis = scene.visuals.XYZAxis(parent=view)
s = STTransform(translate=(50, 50), scale=(50, 50, 50, 1))
affine = s.as_matrix()
axis.transform = affine


def update_axis_visual():
    """Sync XYZAxis visual with camera angles"""
    axis.transform.reset()

    axis.transform.rotate(cam.roll, (0, 0, 1))
    axis.transform.rotate(cam.elevation, (1, 0, 0))
    axis.transform.rotate(cam.azimuth, (0, 1, 0))
    axis.transform.scale((50, 50, 0.001))
    axis.transform.translate((50., 50.))

    axis.update()


update_axis_visual()


@canvas.events.mouse_move.connect
def on_mouse_move(event):
    if event.button == 1 and event.is_dragging:
        update_axis_visual()


if __name__ == '__main__':
    print(__doc__)
    app.run()