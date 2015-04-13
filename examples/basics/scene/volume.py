# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2

"""
Example volume rendering

Controls:

* 1  - toggle camera between first person (fly) and regular 3D (turntable)
* 2  - toggle between volume rendering methods
* 3  - toggle between stent-CT / brain-MRI image
* 4  - toggle between colormaps
* 0  - reset cameras
* [] - decrease/increase isosurface threshold

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
canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)
canvas.measure_fps()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Set whether we are emulating a 3D texture
emulate_texture = True

# Create the volume visuals, only one is visible
volume1 = scene.visuals.Volume(vol1, parent=view.scene, threshold=0.1,
                               emulate_texture=emulate_texture)
volume1.transform = scene.STTransform(translate=(64, 64, 0))
volume2 = scene.visuals.Volume(vol2, parent=view.scene, threshold=0.5,
                               emulate_texture=emulate_texture)
volume2.visible = False

# Create two cameras (1 for firstperson, 3 for 3d person)
fov = 60.
cam1 = scene.cameras.FlyCamera(parent=view.scene, fov=fov)
cam2 = scene.cameras.TurntableCamera(parent=view.scene, fov=fov)
cam3 = scene.cameras.ArcballCamera(parent=view.scene, fov=fov)
view.camera = cam2  # Select turntable at first


# Implement key presses
@canvas.events.key_press.connect
def on_key_press(event):
    if event.text == '1':
        cam_toggle = {cam1: cam2, cam2: cam3, cam3: cam1}
        view.camera = cam_toggle.get(view.camera, 'fly')
    elif event.text == '2':
        methods = ['mip', 'translucent', 'iso', 'additive']
        cmaps = {'mip': 'grays', 'translucent': 'tgrays', 'iso': 'grays', 'additive': 'tgrays'}
        method = methods[(methods.index(volume1.method) + 1) % 4]
        print("Volume render method: %s" % method)
        volume1.method = method
        volume1.cmap = cmaps[method]
        volume2.method = method
        volume2.cmap = cmaps[method]
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
        volume1.threshold -= 0.025
        volume2.threshold = volume1.threshold
    elif event.text == ']':
        volume1.threshold += 0.025
        volume2.threshold = volume1.threshold

# for testing performance
@canvas.connect
def on_draw(ev):
    canvas.update()

if __name__ == '__main__':
    print(__doc__)
    app.run()
