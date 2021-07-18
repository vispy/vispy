# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Display an Image
================

Simple use of SceneCanvas to display an Image.

"""

import sys
from vispy import scene
from vispy import app
from vispy.io import load_data_file, read_png

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create the image
img_data = read_png(load_data_file('mona_lisa/mona_lisa_sm.png'))
interpolation = 'nearest'

image = scene.visuals.Image(img_data, interpolation=interpolation,
                            parent=view.scene, method='subdivide')

canvas.title = 'Spatial Filtering using %s Filter' % interpolation

# Set 2D camera (the camera will scale to the contents in the scene)
view.camera = scene.PanZoomCamera(aspect=1)
# flip y-axis to have correct aligment
view.camera.flip = (0, 1, 0)
view.camera.set_range()
view.camera.zoom(0.1, (250, 200))

# get interpolation functions from Image
names = image.interpolation_functions
names = sorted(names)
act = 17


# Implement key presses
@canvas.events.key_press.connect
def on_key_press(event):
    global act
    if event.key in ['Left', 'Right']:
        if event.key == 'Right':
            step = 1
        else:
            step = -1
        act = (act + step) % len(names)
        interpolation = names[act]
        image.interpolation = interpolation
        canvas.title = 'Spatial Filtering using %s Filter' % interpolation
        canvas.update()


if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
