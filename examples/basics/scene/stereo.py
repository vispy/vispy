# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""
Example demonstrating stereo vision in a scene has an anisotropic aspect
ratio. This example can be used to test that the cameras behave
correctly with nested translated/rotated cameras.

NOTE: This example is currently broken!
"""

import numpy as np

from vispy import app, scene, io

# Read volume
vol1 = np.load(io.load_data_file('volume/stent.npz'))['arr_0']

# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()
canvas.measure_fps()

# Set up a viewbox to display the image with interactive pan/zoom
# Create two ViewBoxes, place side-by-side
vb1 = scene.widgets.ViewBox(border_color='yellow', parent=canvas.scene)
vb2 = scene.widgets.ViewBox(border_color='blue', parent=canvas.scene)

# This is temporarily needed because fragment clipping method is not yet
# compatible with multiple parenting.
vb1.clip_method = 'viewport'
vb2.clip_method = 'viewport'

scenes = vb1.scene, vb2.scene
#
grid = canvas.central_widget.add_grid()
grid.padding = 6
grid.add_widget(vb1, 0, 0)
grid.add_widget(vb2, 0, 1)

# Create the volume visuals, only one is visible
volume1 = scene.visuals.Volume(vol1, parent=scenes, threshold=0.5)

# Create cameras. The second is a child of the first, thus inheriting
# its transform.
cam1 = scene.cameras.TurntableCamera(parent=scenes, fov=60)
cam2 = scene.cameras.PerspectiveCamera(parent=cam1, fov=60)
#
cam2.transform.translate((+10, 0, 0))

vb1.camera = cam1
vb2.camera = cam2

if __name__ == '__main__':
    app.run()
