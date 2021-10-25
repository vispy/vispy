# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2

"""
VolumeVisual
============

Press "r" to switch rendering method.
Press "c" to switch raycasting mode.
"""

from itertools import cycle

import numpy as np

from vispy import app, scene


# create volume
voldata = np.ones((5, 5, 5))
voldata[2:-2, :, :] = 2
voldata[:, 2:-2, :] = 2
voldata[:, :, 2:-2] = 2
voldata[2, 2, 2] = 3

# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)
canvas.measure_fps()
view = canvas.central_widget.add_view()

volume = scene.visuals.Volume(
    voldata,
    interpolation='nearest',
    clim=(0, 4),
    plane_normal=(0, 1, 0),
    plane_position=(0, 2, 0),
    parent=view.scene,
)

# add bounding markers
positions = np.array([
    [0, 0, 0],
    [0, 0, 1],
    [0, 1, 0],
    [0, 1, 1],
    [1, 0, 0],
    [1, 0, 1],
    [1, 1, 0],
    [1, 1, 1],
]) * 5 - 0.5
points = scene.visuals.Markers(pos=positions, parent=view.scene)

cam = scene.cameras.ArcballCamera(parent=view.scene)
view.camera = cam

modes = cycle(['plane', 'volume'])
methods = cycle(['minip', 'translucent', 'additive', 'iso', 'average', 'mip'])


@canvas.events.key_press.connect
def on_key_press(event):
    if event.text == 'r':
        method = next(methods)
        volume.method = method
        print(f'Rendering method: {method}')
    if event.text == 'c':
        mode = next(modes)
        volume.raycasting_mode = mode
        print(f'Rendering mode: {mode}')


if __name__ == '__main__':
    print(__doc__)
    app.run()
