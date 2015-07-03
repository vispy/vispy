# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
This example demonstrates the use of the SurfacePlot visual.
"""

import sys
import numpy as np

from vispy import app, scene
from vispy.util.filter import gaussian_filter


canvas = scene.SceneCanvas(keys='interactive')
view = canvas.central_widget.add_view()
view.camera = scene.TurntableCamera(up='z', fov=60)

# Simple surface plot example
# x, y values are not specified, so assumed to be 0:50
z = np.random.normal(size=(250, 250), scale=200)
z[100, 100] += 50000
z = gaussian_filter(z, (10, 10))
p1 = scene.visuals.SurfacePlot(z=z, color=(0.5, 0.5, 1, 1), shading='smooth')
p1.transform = scene.transforms.MatrixTransform()
p1.transform.scale([1/249., 1/249., 1/249.])
p1.transform.translate([-0.5, -0.5, 0])

view.add(p1)


xax = scene.Axis(pos=[[-0.5, -0.5], [0.5, -0.5]], tick_direction=(0, -1),
                 font_size=16, parent=view.scene)
xax.transform = scene.STTransform(translate=(0, 0, -0.3))

yax = scene.Axis(pos=[[-0.5, -0.5], [-0.5, 0.5]], tick_direction=(-1, 0),
                 font_size=16, parent=view.scene)
yax.transform = scene.STTransform(translate=(0, 0, -0.3))

# Add a 3D axis to keep us oriented
axis = scene.visuals.XYZAxis(parent=view.scene)

if __name__ == '__main__':
    canvas.show()
    if sys.flags.interactive == 0:
        app.run()
