# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2

"""
Complex Volume Rendering
========================

Demonstrates rendering a volume with complex data, where the color is computed
from the raw data based on various complex modes.

Controls:

* 1  - toggle between volume rendering methods
* 2  - toggle between complex modes.
"""

from itertools import cycle
import numpy as np
from vispy import app, scene

def complex_ramp(size=256):
    """Returns a complex array where X ramps phase and Y ramps magnitude."""
    phase_ramp = np.linspace(-np.pi, np.pi - 1 / size, size)
    mag_ramp = np.linspace(10, 0 + 1 / size, size)
    z_ramp = np.linspace(10, 0 + 1 / size, size)
    phase_ramp, mag_ramp, z_ramp = np.meshgrid(phase_ramp, mag_ramp, z_ramp)
    return (mag_ramp * np.exp(1j * phase_ramp) * z_ramp).astype(np.complex64)

vol = complex_ramp()

canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)
canvas.measure_fps()

view = canvas.central_widget.add_view()
volume = scene.visuals.ComplexVolume(vol, parent=view.scene, method='mip', complex_mode='magnitude', cmap='viridis')

cam = scene.cameras.ArcballCamera(parent=view.scene, fov=60)
view.camera = cam

methods = cycle(['attenuated_mip', 'translucent', 'additive', 'average', 'iso', 'mip'])
complex_modes = cycle(['phase', 'real', 'imaginary', 'magnitude'])


print("Render method: mip")
print("Complex mode: magnitude")

@canvas.events.key_press.connect
def on_key_press(event):
    if event.text == '1':
        method = next(methods)
        volume.method = method
        print(f"Render method: {method}")
    elif event.text == '2':
        mode = next(complex_modes)
        volume.complex_mode = mode
        print(f"Complex mode: {mode}")


if __name__ == '__main__':
    print(__doc__)
    app.run()
