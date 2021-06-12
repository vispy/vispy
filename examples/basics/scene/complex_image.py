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
from vispy import app, scene


def complex_ramp(size=512, phase_range=(-np.pi, np.pi), mag_range=(0, 10)):
    """Returns a complex array where X ramps phase and Y ramps magnitude."""
    p0, p1 = phase_range
    phase_ramp = np.linspace(p0, p1 - 1 / size, size)
    m0, m1 = mag_range
    mag_ramp = np.linspace(m1, m0 + 1 / size, size)
    phase_ramp, mag_ramp = np.meshgrid(phase_ramp, mag_ramp)
    return mag_ramp * np.exp(1j * phase_ramp)


canvas = scene.SceneCanvas(keys="interactive")
canvas.size = 512, 512
canvas.show()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create the image
img_data = complex_ramp().astype(np.complex64)

# View it with "complex_mode=imaginary" 
image = scene.visuals.Image(
    img_data,
    texture_format="auto",
    clim=(-10, 10),
    parent=view.scene,
    complex_mode="imaginary",
)

# Set 2D camera (the camera will scale to the contents in the scene)
view.camera = scene.PanZoomCamera(aspect=1)
view.camera.set_range()
view.camera.zoom(1)


if __name__ == "__main__" and sys.flags.interactive == 0:
    app.run()
