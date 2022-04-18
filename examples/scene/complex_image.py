# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Complex image data
==================

Simple use of SceneCanvas to display an image consisting of complex numbers.

The left and right arrow keys can be used to cycle the view between the real,
imaginary, phase, or magnitude of the data.

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
    return (mag_ramp * np.exp(1j * phase_ramp)).astype(np.complex64)


canvas = scene.SceneCanvas(keys="interactive",
                           title="Complex number view: phase")
canvas.size = 512, 512
canvas.show()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create the image
img_data = complex_ramp()

# View it with "complex_mode=imaginary"
image = scene.visuals.ComplexImage(img_data, parent=view.scene, complex_mode="phase")

# Set 2D camera (the camera will scale to the contents in the scene)
view.camera = scene.PanZoomCamera(aspect=1)
view.camera.set_range()
view.camera.zoom(1)


complex_modes = [
    "real",
    "imaginary",
    "magnitude",
    "phase",
]
mode_index = 3


@canvas.connect
def on_key_press(event):
    global mode_index
    if event.key not in ['Left', 'Right']:
        return

    if event.key == 'Right':
        step = 1
    else:
        step = -1
    mode_index = (mode_index + step) % len(complex_modes)
    complex_mode = complex_modes[mode_index]
    image.complex_mode = complex_mode
    canvas.title = f'Complex number view: {complex_mode}'
    canvas.update()


if __name__ == "__main__" and sys.flags.interactive == 0:
    app.run()
