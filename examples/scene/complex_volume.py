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


def complex_ramp(size=512):
    """Returns a complex array where X ramps phase and Y ramps magnitude."""
    phase_ramp = np.linspace(-np.pi, np.pi - 1 / size, size)
    mag_ramp = np.linspace(10, 0 + 1 / size, size)
    z_ramp = np.linspace(10, 0 + 1 / size, size)
    phase_ramp, mag_ramp, z_ramp = np.meshgrid(phase_ramp, mag_ramp, z_ramp)
    return (mag_ramp * np.exp(1j * phase_ramp) * z_ramp).astype(np.complex64)


canvas = scene.SceneCanvas(keys="interactive", size=(512, 512), show=True)

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

cam = scene.cameras.TurntableCamera(parent=view.scene, fov=60, name="Turntable")
# cam = scene.cameras.ArcballCamera(parent=view.scene, fov=60, name='Arcball')
view.camera = cam

# Create the image
img_data = complex_ramp()

image = scene.visuals.ComplexVolume(
    img_data.real, parent=view.scene, complex_mode="magnitude"
)

# Set 2D camera (the camera will scale to the contents in the scene)
view.camera = scene.PanZoomCamera(aspect=1)
view.camera.set_range()
view.camera.zoom(1)


if __name__ == "__main__" and sys.flags.interactive == 0:
    app.run()
