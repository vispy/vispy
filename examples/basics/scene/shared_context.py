# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
This example demonstrates the use of multiple canvases with visuals shared 
between them.
"""

import sys
import numpy as np

from vispy import app, scene
from vispy.util.filter import gaussian_filter


canvas1 = scene.SceneCanvas(keys='interactive', show=True)
view1 = canvas1.central_widget.add_view()
view1.set_camera('turntable', mode='perspective', up='z', distance=2,
                 azimuth=30., elevation=30.)

canvas2 = scene.SceneCanvas(keys='interactive', show=True)
view2 = canvas2.central_widget.add_view()
view2.set_camera('panzoom')

## Simple surface plot example
## x, y values are not specified, so assumed to be 0:50
z = gaussian_filter(np.random.normal(size=(50, 50)), (1, 1)) * 10
p1 = scene.visuals.SurfacePlot(z=z, color=(0.5, 0.5, 1, 1), shading='smooth')
p1.transform = scene.transforms.AffineTransform()
p1.transform.scale([1/49., 1/49., 0.02])
p1.transform.translate([-0.5, -0.5, 0])

view1.add(p1)
view2.add(p1)

# Add a 3D axis to keep us oriented
axis = scene.visuals.XYZAxis(parent=view1.scene)

if __name__ == '__main__':
    if sys.flags.interactive == 0:
        app.run()
