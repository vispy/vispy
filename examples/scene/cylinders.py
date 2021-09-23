# -*- coding: utf-8 -*-
# vispy: gallery 10
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Create a Point Cloud
====================

Demonstrates use of visual.Markers to create a point cloud with a
standard turntable camera to fly around with and a centered 3D Axis.
"""

import numpy as np
import vispy.scene
from vispy import gloo
from vispy.scene import visuals


gloo.gl.use_gl('gl+')

#
# Make a canvas and add simple view
#
canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view()

# generate data
np.random.seed(1)
pos = np.random.normal(size=(100, 3), scale=0.2) * 100
color = np.random.rand(100, 3)
size = np.random.rand(100) * 5

# create scatter object and fill in the data
scatter = visuals.Markers()
scatter.set_data(pos, face_color=color)

cyl = visuals.Cylinders()
cyl.set_data(pos, color=color, width=size)

view.add(scatter)
view.add(cyl)

view.camera = 'arcball'  # or try 'arcball'
view.camera.fov = 0

# add a colored 3D axis for orientation
axis = visuals.XYZAxis(parent=view.scene)

if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
