# -*- coding: utf-8 -*-
# vispy: gallery 10
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Create a bunch of Cylinders
===========================
"""

import numpy as np
import vispy.scene
from vispy import gloo
from vispy.scene import visuals

gloo.gl.use_gl('gl+')

canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view()

# generate data
np.random.seed(1)
pos = np.random.normal(size=(100, 3), scale=0.2) * 100
color = np.random.rand(100, 3)
width = 5

# create markers for visual aid
scatter = visuals.Markers(pos=pos, face_color=color)

# create cylinders
cyl = visuals.Cylinders(pos=pos, color=color, width=width)

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
