# -*- coding: utf-8 -*-
# vispy: gallery-exports animation.gif
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Create and Save Animation
=========================

This example demonstrates how to create a sphere.
"""

import imageio

from vispy import scene
from vispy.visuals.transforms import STTransform

output_filename = 'animation.gif'
n_steps = 18
step_angle = 10.
axis = [0, 0.707, 0.707]

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white',
                           size=(800, 600), show=True)

view = canvas.central_widget.add_view()
view.camera = 'arcball'

sphere1 = scene.visuals.Sphere(radius=1, method='latitude', parent=view.scene,
                               edge_color='black')

sphere2 = scene.visuals.Sphere(radius=1, method='ico', parent=view.scene,
                               edge_color='black')

sphere3 = scene.visuals.Sphere(radius=1, rows=10, cols=10, depth=10,
                               method='cube', parent=view.scene,
                               edge_color='black')

sphere1.transform = STTransform(translate=[-2.5, 0, 0])
sphere3.transform = STTransform(translate=[2.5, 0, 0])

view.camera.set_range(x=[-3, 3])

writer = imageio.get_writer('animation.gif')
for i in range(n_steps * 2):
    im = canvas.render(alpha=True)
    writer.append_data(im)
    if i >= n_steps:
        view.camera.transform.rotate(step_angle, axis)
    else:
        view.camera.transform.rotate(-step_angle, axis)
writer.close()
