# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Simple use of SceneCanvas to display an Image.
"""
import sys
from vispy import scene
from vispy import app
import numpy as np
from itertools import cycle

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create the image
#img_data = np.random.normal(size=(100, 100, 3), loc=128,
#                            scale=50).astype(np.ubyte)
img_data = np.zeros(25).reshape((5, 5)).astype(np.float32)
img_data[1:4, 1::2] = 0.5
img_data[1::2, 2] = 0.5
img_data[2, 2] = 1.0
ipol = 'Nearest'
image = scene.visuals.Image(img_data, ipol=ipol, parent=view.scene)
canvas.title = 'Spatial Filtering using %s Filter' % ipol
# Set 2D camera (the camera will scale to the contents in the scene)
view.camera = scene.PanZoomCamera(aspect=1)
view.camera.set_range()

names = cycle(image._names)

# Implement key presses
@canvas.events.key_press.connect
def on_key_press(event):
    ipol = next(names)
    image.ipol = ipol
    canvas.title = 'Spatial Filtering using %s Filter' % ipol
    canvas.update()


if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
