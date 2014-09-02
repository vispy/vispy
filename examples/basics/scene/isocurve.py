# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Simple use of SceneCanvas to display an Isocurve visual.
"""
from vispy import app, scene
from vispy.util.filter import gaussian_filter
import numpy as np

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create the image
img_data = np.empty((100, 100, 3), dtype=np.ubyte)
noise = np.random.normal(size=(100, 100), loc=50, scale=150)
noise = gaussian_filter(noise, (4, 4, 0))
img_data[:] = noise[..., np.newaxis]
image = scene.visuals.Image(img_data, parent=view.scene)

# Create isocurve, make a child of the image to ensure the two are always
# aligned.
curve1 = scene.visuals.Isocurve(noise, level=60, color=(0, 0, 1, 1), 
                                parent=view.scene)
curve2 = scene.visuals.Isocurve(noise, level=50, color=(0, 0, 0.5, 1), 
                                parent=view.scene)
curve3 = scene.visuals.Isocurve(noise, level=40, color=(0, 0, 0.3, 1), 
                                parent=view.scene)

# Set the view bounds to show the entire image with some padding
view.camera.rect = (-10, -10, image.size[0]+20, image.size[1]+20)


import sys
if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
