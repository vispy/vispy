# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Simple use of SceneCanvas to display an Image.
"""
import sys

import numpy as np
from scipy.fftpack import fftn, fftshift
from vispy import app, scene
from vispy.io import load_data_file, read_png

canvas = scene.SceneCanvas(keys="interactive")
canvas.size = 800, 600
canvas.show()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create the image
img_data = read_png(load_data_file("mona_lisa/mona_lisa_sm.png"))
interpolation = "nearest"

img_data = np.log(fftshift(fftn(img_data.mean(-1)).astype("complex64")))

image = scene.visuals.Image(
    img_data,
    interpolation=interpolation,
    texture_format="auto",
    clim=(11, 22),
    gamma=0.8,
    parent=view.scene,
)

# Set 2D camera (the camera will scale to the contents in the scene)
view.camera = scene.PanZoomCamera(aspect=1)
view.camera.set_range()
view.camera.zoom(0.5)


if __name__ == "__main__" and sys.flags.interactive == 0:
    app.run()
