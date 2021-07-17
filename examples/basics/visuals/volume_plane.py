# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2
"""
Example volume rendering with plane rendering

Controls:
* 1  - toggle between volume rendering methods
* 2 -  toggle between volume rendering modes ('volume', 'plane')
* [] - shift along plane normal
* {} - decrease/increase plane thickness

* x/y/z/o - set plane normal along x/y/z or [1,1,1] oblique axis
"""
import numpy as np

from vispy import app, scene, io
from vispy.visuals.transforms import STTransform

# Read volume
vol = np.load(io.load_data_file('volume/stent.npz'))['arr_0']

# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create the volume visual
volume = scene.visuals.Volume(vol, parent=view.scene, raycasting_mode='plane')
volume.transform = scene.STTransform(translate=(64, 64, 0))

# Create a camera
fov = 60.
cam = scene.cameras.TurntableCamera(parent=view.scene, fov=fov, name='Turntable')

view.camera = cam

# Create an XYZAxis visual
axis = scene.visuals.XYZAxis(parent=view)
s = STTransform(translate=(50, 50), scale=(50, 50, 50, 1))
affine = s.as_matrix()
axis.transform = affine


# Implement axis connection with cam2
@canvas.events.mouse_move.connect
def on_mouse_move(event):
    if event.button == 1 and event.is_dragging:
        axis.transform.reset()

        axis.transform.rotate(cam.roll, (0, 0, 1))
        axis.transform.rotate(cam.elevation, (1, 0, 0))
        axis.transform.rotate(cam.azimuth, (0, 1, 0))

        axis.transform.scale((50, 50, 0.001))
        axis.transform.translate((50., 50.))
        axis.update()


# Implement key presses
@canvas.events.key_press.connect
def on_key_press(event):
    if event.text == '1':
        methods = ['mip', 'average']
        method = methods[(methods.index(volume.method) + 1) % 2]
        print("Volume render method: %s" % method)
        volume.method = method
    elif event.text == '2':
        modes = ['volume', 'plane']
        if volume.raycasting_mode == modes[0]:
            volume.raycasting_mode = modes[1]
            print(modes[1])
        else:
            volume.raycasting_mode = modes[0]
            print(modes[0])
    elif event.text != '' and event.text in '{}':
        t = -1 if event.text == '{' else 1
        volume.plane_thickness += t
        volume.plane_thickness += t
        print(f"plane thickness: {volume.plane_thickness}")
    elif event.text != '' and event.text in '[]':
        shift = volume.plane_normal / np.linalg.norm(volume.plane_normal)
        if event.text == '[':
            volume.plane_position -= 2 * shift
        elif event.text == ']':
            volume.plane_position += 2 * shift
        print(f"plane position: {volume.plane_position}")

    elif event.text == 'x':
        volume.plane_normal = [0, 0, 1]
    elif event.text == 'y':
        volume.plane_normal = [0, 1, 0]
    elif event.text == 'z':
        volume.plane_normal = [1, 0, 0]
    elif event.text == 'o':
        volume.plane_normal = [1, 1, 1]


if __name__ == '__main__':
    print(__doc__)
    app.run()
