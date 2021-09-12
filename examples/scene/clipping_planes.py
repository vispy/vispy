# -*- coding: utf-8 -*-
# vispy: gallery 5
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Clipping planes with volume and markers
=======================================
Controls:
- x/y/z/o - add new clipping plane with normal along x/y/z or [1,1,1] oblique axis
- r - remove a clipping plane
"""

import numpy as np

from vispy import app, scene, io
from vispy.visuals.transforms import STTransform
from vispy.visuals.filters.clipping_planes import PlanesClipper

# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create the visuals
vol = np.load(io.load_data_file('volume/stent.npz'))['arr_0']
volume = scene.visuals.Volume(vol, parent=view.scene, threshold=0.225)

np.random.seed(1)
points = np.random.rand(100, 3) * (128, 128, 128)
markers = scene.visuals.Markers(pos=points, parent=view.scene)
# add a transform to markers, to show clipping is in scene coordinates
markers.transform = scene.STTransform(translate=(0, 0, 128))

# Create the clipping planes filter for the markers (Volume has its own clipping logic)
clipper = PlanesClipper()
# and attach it to the markers
markers.attach(clipper)

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


# Implement axis connection with cam2
@canvas.events.mouse_move.connect
def on_mouse_move(event):
    if event.button == 1 and event.is_dragging:
        axis.transform.reset()

        axis.transform.rotate(cam.roll, (0, 0, 1))
        axis.transform.rotate(cam.elevation, (1, 0, 0))
        axis.transform.rotate(cam.azimuth, (0, 1, 0))

        axis.transform.scale((50, 50, 0.001))
        axis.transform.translate((50., 50.))
        axis.update()


volume_center = (np.array(vol.shape) / 2)

# clipping planes around the origin
clip_modes = {
    'x': np.array([[volume_center, [0, 0, 1]]]),
    'y': np.array([[volume_center, [0, 1, 0]]]),
    'z': np.array([[volume_center, [1, 0, 0]]]),
    'o': np.array([[volume_center, [1, 1, 1]]]),
}


def add_clip(mode):
    if mode not in clip_modes:
        return
    new_plane = clip_modes[mode]
    if volume.clipping_planes is None:
        clipping_planes = new_plane
    else:
        clipping_planes = np.concatenate([volume.clipping_planes, new_plane])
    volume.clipping_planes = clipping_planes
    clipper.clipping_planes = clipping_planes


def remove_clip():
    if volume.clipping_planes is not None:
        volume.clipping_planes = volume.clipping_planes[:-1]
        clipper.clipping_planes = clipper.clipping_planes[:-1]


# Implement key presses
@canvas.events.key_press.connect
def on_key_press(event):
    if event.text in 'xyzo':
        add_clip(event.text)
    elif event.text == 'r':
        remove_clip()


if __name__ == '__main__':
    print(__doc__)
    app.run()
