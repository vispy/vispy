# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2

"""
Example volume rendering

Controls:

* 1 - toggle camera between first person (fly) and regular 3D (turntable)
* 2 - toggle between mip and iso render styles
* 3 - toggle between stent-CT / brain-MRI image
* 4 - toggle between colormaps
* 0 - reset cameras

With fly camera:

* WASD or arrow keys - move around
* SPACE - brake
* FC - move up-down
* IJKL or mouse - look around
"""

from itertools import cycle

import numpy as np

from vispy import app, scene, io
from vispy.color import get_colormaps

# Read volume
vol1 = np.load(io.load_data_file('volume/stent.npz'))['arr_0']
vol2 = np.load(io.load_data_file('brain/mri.npz'))['data']
vol2 = np.flipud(np.rollaxis(vol2, 1))

# Setup colormaps
cmaps = cycle(get_colormaps())

# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()
canvas.measure_fps()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create the volume visuals, only one is visible
volume1 = scene.visuals.Volume(vol1, parent=view.scene, threshold=0.5)
volume1.transform = scene.STTransform(translate=(64, 64, 0))
volume2 = scene.visuals.Volume(vol2, parent=view.scene, threshold=0.5)
volume2.visible = False

# Create two cameras (1 for firstperson, 3 for 3d person)
cam1 = scene.cameras.FlyCamera(parent=view.scene)
cam3 = scene.cameras.TurntableCamera(parent=view.scene)
view.camera = cam3  # Select turntable at first


# Implement key presses
@canvas.events.key_press.connect
def on_key_press(event):
    if event.text == '1':
        cam_toggle = {cam1: cam3, cam3: cam1}
        view.camera = cam_toggle.get(view.camera, 'fly')
    elif event.text == '2':
        style_toggle = {'mip': 'iso', 'iso': 'mip'}
        volume1.style = style_toggle.get(volume1.style, 'mip')
        volume2.style = volume1.style
    elif event.text == '3':
        volume1.visible = not volume1.visible
        volume2.visible = not volume1.visible
    elif event.text == '4':
        cmap = next(cmaps)
        volume1.cmap = cmap
        volume2.cmap = cmap
    elif event.text == '0':
        cam1.set_range()
        cam3.set_range()
    elif event.text == '[':
        volume1.threshold -= 0.1
        volume2.threshold = volume1.threshold
    elif event.text == ']':
        volume1.threshold += 0.1
        volume2.threshold = volume1.threshold

if __name__ == '__main__':
    print(__doc__)
    app.run()
