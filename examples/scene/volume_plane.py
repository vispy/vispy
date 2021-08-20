# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 10:200:5
"""
Rendering Planes through 3D Data
================================

Controls:
* 1  - toggle between volume rendering methods
* 2 -  toggle between volume rendering modes ('volume', 'plane')
* [] - shift plane along plane normal
* {} - decrease/increase plane thickness
* Spacebar - stop/start animation

* x/y/z/o - set plane normal along x/y/z or [1,1,1] oblique axis
"""
import sys

import numpy as np

from vispy import app, scene, io
from vispy.visuals.transforms import STTransform

# Read volume
vol = np.load(io.load_data_file('volume/stent.npz'))['arr_0']

# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view()

# Create the volume visual for plane rendering
plane = scene.visuals.Volume(
    vol,
    parent=view.scene,
    raycasting_mode='plane',
    method='mip',
    plane_thickness=3.0,
    plane_position=(128, 60, 64),
    plane_normal=(1, 0, 0),
)

volume = scene.visuals.Volume(
    vol,
    parent=view.scene,
    raycasting_mode='volume',
    method='mip',
)
volume.set_gl_state('additive')
volume.opacity = 0.25

# Create a camera
cam = scene.cameras.TurntableCamera(
    parent=view.scene, fov=60.0, azimuth=-42.0, elevation=30.0
)
view.camera = cam

# Create an XYZAxis visual
axis = scene.visuals.XYZAxis(parent=view)
s = STTransform(translate=(50, 50), scale=(50, 50, 50, 1))
affine = s.as_matrix()
axis.transform = affine


def update_axis_visual():
    """Sync XYZAxis visual with camera angles"""
    axis.transform.reset()

    axis.transform.rotate(cam.roll, (0, 0, 1))
    axis.transform.rotate(cam.elevation, (1, 0, 0))
    axis.transform.rotate(cam.azimuth, (0, 1, 0))
    axis.transform.scale((50, 50, 0.001))
    axis.transform.translate((50., 50.))

    axis.update()


update_axis_visual()


@canvas.events.mouse_move.connect
def on_mouse_move(event):
    if event.button == 1 and event.is_dragging:
        update_axis_visual()


# Implement key presses
@canvas.events.key_press.connect
def on_key_press(event):
    if event.text == '1':
        methods = ['mip', 'average']
        method = methods[(methods.index(plane.method) + 1) % 2]
        print("Volume render method: %s" % method)
        plane.method = method
    elif event.text == '2':
        modes = ['volume', 'plane']
        if plane.raycasting_mode == modes[0]:
            plane.raycasting_mode = modes[1]
            print(modes[1])
        else:
            plane.raycasting_mode = modes[0]
            print(modes[0])
    elif event.text != '' and event.text in '{}':
        t = -1 if event.text == '{' else 1
        plane.plane_thickness += t
        plane.plane_thickness += t
        print(f"plane thickness: {plane.plane_thickness}")
    elif event.text != '' and event.text in '[]':
        shift = plane.plane_normal / np.linalg.norm(plane.plane_normal)
        if event.text == '[':
            plane.plane_position -= 2 * shift
        elif event.text == ']':
            plane.plane_position += 2 * shift
        print(f"plane position: {plane.plane_position}")
    elif event.text == 'x':
        plane.plane_normal = [0, 0, 1]
    elif event.text == 'y':
        plane.plane_normal = [0, 1, 0]
    elif event.text == 'z':
        plane.plane_normal = [1, 0, 0]
    elif event.text == 'o':
        plane.plane_normal = [1, 1, 1]
    elif event.text == ' ':
        if timer.running:
            timer.stop()
        else:
            timer.start()


def move_plane(event):
    z_pos = plane.plane_position[0]
    if z_pos < 32:
        plane.plane_position = plane.plane_position + [1, 0, 0]
    elif 32 < z_pos <= 220:
        plane.plane_position = plane.plane_position - [1, 0, 0]
    else:
        plane.plane_position = (220, 64, 64)


timer = app.Timer('auto', connect=move_plane, start=True)

if __name__ == '__main__':
    canvas.show()
    print(__doc__)
    if sys.flags.interactive == 0:
        plane.plane_position = (220, 64, 64)
        app.run()
