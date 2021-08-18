# -*- coding: utf-8 -*-
# vispy: gallery 10
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Interactively clip a Point Cloud with clipping planes
=====================================================
Controls:
- x/y/z/o - add new clipping plane with normal along x/y/z or [1,1,1] oblique axis
- r - remove a clipping plane
"""

import numpy as np
import vispy.scene
from vispy.scene import visuals

#
# Make a canvas and add simple view
#
canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view()


# generate data
pos = np.random.normal(size=(100000, 3), scale=0.2)
# one could stop here for the data generation, the rest is just to make the
# data look more interesting. Copied over from magnify.py
centers = np.random.normal(size=(50, 3))
indexes = np.random.normal(size=100000, loc=centers.shape[0]/2.,
                           scale=centers.shape[0]/3.)
indexes = np.clip(indexes, 0, centers.shape[0]-1).astype(int)
scales = 10**(np.linspace(-2, 0.5, centers.shape[0]))[indexes][:, np.newaxis]
pos *= scales
pos += centers[indexes]

# create scatter object and fill in the data
scatter = visuals.Markers()
scatter.set_data(pos, edge_color=None, face_color=(1, 1, 1, .5), size=5)

view.add(scatter)

view.camera = 'turntable'  # or try 'arcball'

# add a colored 3D axis for orientation
axis = visuals.XYZAxis(parent=view.scene)

points_center = [0, 0, 0]

clip_modes = {
    'x': np.array([[points_center, [0, 0, 1]]]),
    'y': np.array([[points_center, [0, 1, 0]]]),
    'z': np.array([[points_center, [1, 0, 0]]]),
    'o': np.array([[points_center, [1, 1, 1]]]),
}


def add_clip(points, mode):
    if mode in clip_modes:
        new_plane = clip_modes[mode]
        if points.clipping_planes is None:
            points.clipping_planes = new_plane
        else:
            points.clipping_planes = np.concatenate([points.clipping_planes, new_plane])


def remove_clip(points):
    if points.clipping_planes is not None:
        points.clipping_planes = points.clipping_planes[:-1]


# Implement key presses
@canvas.events.key_press.connect
def on_key_press(event):
    if event.text in 'xyzo':
        add_clip(scatter, event.text)
    elif event.text == 'r':
        remove_clip(scatter)


if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
