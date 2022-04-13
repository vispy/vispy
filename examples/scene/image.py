# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Display an Image
================

Simple use of SceneCanvas to display an Image.

"""

import sys
from itertools import cycle
from vispy import scene
from vispy import app
from vispy.io import load_data_file, read_png
from scipy.signal.windows import gaussian
import numpy as np

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create the image
img_data = read_png(load_data_file('mona_lisa/mona_lisa_sm.png'))
interpolation = 'nearest'

gaussian_window = gaussian(10, 5)
gaussian_kernel = np.outer(gaussian_window, gaussian_window)

h_prewitt_kernel = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
v_prewitt_kernel = h_prewitt_kernel.T

kernels = cycle([gaussian_kernel, h_prewitt_kernel, v_prewitt_kernel])

image = scene.visuals.Image(
    img_data, interpolation=interpolation, parent=view.scene,
    method='subdivide', custom_kernel=next(kernels)
)

canvas.title = 'Spatial Filtering using %s Filter' % interpolation

# Set 2D camera (the camera will scale to the contents in the scene)
view.camera = scene.PanZoomCamera(aspect=1)
# flip y-axis to have correct aligment
view.camera.flip = (0, 1, 0)
view.camera.set_range()
view.camera.zoom(0.1, (250, 200))

# get interpolation functions from Image
names = image.interpolation_functions
names = sorted(names)


# Implement key presses
@canvas.events.key_press.connect
def on_key_press(event):
    if event.key in ['Left', 'Right']:
        step = 1 if event.key == 'Right' else -1
        idx = (names.index(image.interpolation) + step) % len(names)
        interpolation = names[idx]
        image.interpolation = interpolation
        canvas.title = 'Spatial Filtering using %s Filter' % interpolation
        canvas.update()
    elif event.key == 'k':
        image.custom_kernel = next(kernels)


if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
