# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

# For testing zoom sensitivity on various platforms

import numpy as np
import vispy.scene
from vispy.scene import visuals

canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
vb = canvas.central_widget.add_view()
vb.camera = 'panzoom'
vb.camera.rect = (-10, -10, 20, 20)

centers = np.random.normal(size=(50, 2))
pos = np.random.normal(size=(100000, 2), scale=0.2)
indexes = np.random.normal(size=100000, loc=centers.shape[0]/2., 
                           scale=centers.shape[0]/3.)
indexes = np.clip(indexes, 0, centers.shape[0]-1).astype(int)
scales = 10**(np.linspace(-2, 0.5, centers.shape[0]))[indexes][:, np.newaxis]
pos *= scales
pos += centers[indexes]

scatter = visuals.Markers()
scatter.set_gl_state('translucent', depth_test=False)
scatter.set_data(pos, edge_width=0, face_color=(1, 1, 1, 0.3), size=5)
vb.add(scatter)


@canvas.connect
def on_key_press(ev):
    if ev.key.name in '+=':
        vb.camera.zoom_factor *= 1.1
    elif ev.key.name == '-':
        vb.camera.zoom_factor /= 1.1
    print("Zoom factor: %0.4f" % vb.camera.zoom_factor)


if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
