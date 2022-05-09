# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Custom image sampling
=====================

Use custom interpolation kernels for image sampling.

Press k to switch kernel.
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

# build custom kernels
small_gaussian_window = gaussian(5, 1)
small_gaussian_kernel = np.outer(small_gaussian_window, small_gaussian_window)

big_gaussian_window = gaussian(20, 10)
big_gaussian_kernel = np.outer(big_gaussian_window, big_gaussian_window)

h_prewitt_kernel = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
v_prewitt_kernel = h_prewitt_kernel.T

kernels = {
    'null': np.ones((1, 1)),
    'small gaussian': small_gaussian_kernel,
    'big gaussian': big_gaussian_kernel,
    'horizontal prewitt': h_prewitt_kernel,
    'vertical prewitt': v_prewitt_kernel,
}

k_names = cycle(kernels.keys())

k = next(k_names)

image = scene.visuals.Image(
    img_data,
    interpolation='custom',
    custom_kernel=kernels[k],
    parent=view.scene,
)

canvas.title = f'Custom sampling with {k} kernel'

# Set 2D camera (the camera will scale to the contents in the scene)
view.camera = scene.PanZoomCamera(aspect=1)
# flip y-axis to have correct aligment
view.camera.flip = (0, 1, 0)
view.camera.set_range()


# Implement key presses
@canvas.events.key_press.connect
def on_key_press(event):
    if event.key == 'k':
        k = next(k_names)
        image.custom_kernel = kernels[k]
        canvas.title = f'Custom sampling with {k} kernel'
        canvas.update()


if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
    print(__doc__)
