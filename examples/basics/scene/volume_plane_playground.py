# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2
import mrcfile
"""
Example volume rendering

Controls:
* 1  - toggle between volume rendering methods
* 2 -  toggle between volume rendering modes
* [] - shift along plane normal
* {} - decrease/increase plane thickness
With fly camera:

* WASD or arrow keys - move around
* SPACE - brake
* FC - move up-down
* IJKL or mouse - look around
"""

from itertools import cycle

import numpy as np

from vispy import app, scene, io
from vispy.color import get_colormaps, BaseColormap
from vispy.visuals.transforms import STTransform

# Read volume
# vol = np.load(io.load_data_file('volume/stent.npz'))['arr_0']
HIV = '/Users/aburt/Playground/visualise_particles/TS_01.mrc_10.00Apx.mrc'
CELL = '/Users/aburt/Playground/visualise_particles/Liang_denoised_mycoplasma/00287_10.00Apx_denoised.mrc'
vol = mrcfile.open(HIV).data * -1

# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)
canvas.measure_fps()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Set whether we are emulating a 3D texture
emulate_texture = False

# Create the volume visuals, only one is visible
volume = scene.visuals.Volume(vol, parent=view.scene, threshold=0.225,
                               emulate_texture=emulate_texture, mode='plane')
volume.transform = scene.STTransform(translate=(64, 64, 0))

# Create three cameras (Fly, Turntable and Arcball)
fov = 60.
cam = scene.cameras.TurntableCamera(parent=view.scene, fov=fov,
                                     name='Turntable')

view.camera = cam  # Select turntable at first

# Create an XYZAxis visual
axis = scene.visuals.XYZAxis(parent=view)
s = STTransform(translate=(50, 50), scale=(50, 50, 50, 1))
affine = s.as_matrix()
axis.transform = affine


# create colormaps that work well for translucent and additive volume rendering
class TransFire(BaseColormap):
    glsl_map = """
    vec4 translucent_fire(float t) {
        return vec4(pow(t, 0.5), t, t*t, max(0, t*1.05 - 0.05));
    }
    """


class TransGrays(BaseColormap):
    glsl_map = """
    vec4 translucent_grays(float t) {
        return vec4(t, t, t, t*0.05);
    }
    """

# Setup colormap iterators
opaque_cmaps = cycle(get_colormaps())
translucent_cmaps = cycle([TransFire(), TransGrays()])
opaque_cmap = next(opaque_cmaps)
translucent_cmap = next(translucent_cmaps)


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
        methods = ['mip', 'average', 'minip']
        method = methods[(methods.index(volume.method) + 1) % 3]
        print("Volume render method: %s" % method)
        volume.method = method
    elif event.text == '2':
        modes = ['volume', 'plane']
        if volume.mode == modes[0]:
            volume.mode = modes[1]
            print(modes[1])
        else:
            volume.mode = modes[0]
            print(modes[1])
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


# for testing performance
# @canvas.connect
# def on_draw(ev):
# canvas.update()

if __name__ == '__main__':
    print(__doc__)
    app.run()
