# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2

"""
RGB Volume Rendering
====================

Demonstrates rendering a volume with RGB data, where the color is encoded
directly in the data rather than mapped through a colormap.

Three overlapping Gaussian blobs (red, green, blue) are rendered using
different volume rendering methods.

Controls:

* 1  - toggle between volume rendering methods
* 2  - toggle between turntable and arcball cameras
"""

from itertools import cycle

import numpy as np

from vispy import app, scene


def make_rgb_volume(shape=(80, 80, 80)):
    """Create a volume with three colored Gaussian blobs."""
    vol = np.zeros(shape + (3,), dtype=np.float32)
    zz, yy, xx = np.mgrid[:shape[0], :shape[1], :shape[2]]
    cx, cy, cz = [s // 2 for s in shape]
    sigma = min(shape) / 4

    # Red blob offset in +x
    d2 = (xx - cx - 10) ** 2 + (yy - cy) ** 2 + (zz - cz) ** 2
    vol[..., 0] = np.exp(-d2 / (2 * sigma ** 2))

    # Green blob offset in +y
    d2 = (xx - cx) ** 2 + (yy - cy - 10) ** 2 + (zz - cz) ** 2
    vol[..., 1] = np.exp(-d2 / (2 * sigma ** 2))

    # Blue blob offset in +z
    d2 = (xx - cx) ** 2 + (yy - cy) ** 2 + (zz - cz - 10) ** 2
    vol[..., 2] = np.exp(-d2 / (2 * sigma ** 2))

    return vol


vol = make_rgb_volume()

canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)
canvas.measure_fps()

view = canvas.central_widget.add_view()
volume = scene.visuals.Volume(vol, parent=view.scene, method='mip')

cam1 = scene.cameras.TurntableCamera(parent=view.scene, fov=60,
                                     name='Turntable')
cam2 = scene.cameras.ArcballCamera(parent=view.scene, fov=60,
                                   name='Arcball')
view.camera = cam1

methods = cycle(['mip', 'translucent', 'additive', 'average'])


@canvas.events.key_press.connect
def on_key_press(event):
    if event.text == '1':
        method = next(methods)
        volume.method = method
        print("Render method: %s" % method)
    elif event.text == '2':
        cam_toggle = {cam1: cam2, cam2: cam1}
        view.camera = cam_toggle.get(view.camera, cam1)
        print(view.camera.name + ' camera')


if __name__ == '__main__':
    print(__doc__)
    app.run()
