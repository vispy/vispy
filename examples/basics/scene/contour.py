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
from vispy import visuals
from vispy.util.filter import gaussian_filter
from vispy.visuals.filters import Isoline
import numpy as np
from vispy.io import load_data_file, read_png

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create the image
interpolation = 'bicubic'
np.random.seed(1000)
img_data = np.random.normal(size=(100, 100), loc=50, scale=150)
img_data = gaussian_filter(img_data, (4, 4, 0)).astype(np.float32)

img_data = np.zeros(25).reshape((5, 5)).astype(np.float32)
img_data[1:4, 1::2] = 0.5
img_data[1::2, 2] = 0.5
img_data[2, 2] = 1.0

img_data = read_png(load_data_file('mona_lisa/mona_lisa_sm.png'))
#img_data = np.dot(img_data[...,:3], [0.299, 0.587, 0.144])
#img_data = img_data[...,0] * img_data[...,1] * img_data[...,2]
#img_data /= 3.
#image = scene.visuals.Image(img_data, interpolation=interpolation,
#                            parent=view.scene, method='subdivide')

img_data1 = np.zeros((100, 100))
img_data1[0,0] = -0.5
img_data1[99,99] = +0.5
image = scene.visuals.Image(img_data, interpolation=interpolation,
                            parent=view.scene, method='subdivide')

#image = scene.visuals.Contour(img_data, interpolation='bicubic1',
#                            parent=view.scene, method='subdivide',
#                            levels=2, width=1.0, color='yellow')

image.transform = visuals.transforms.STTransform(translate=(0, 0, 0.5))

levels = np.linspace(img_data.min(), img_data.max(), num=13, endpoint=True)[1:-1]
color_lev = 'white'
# Create isocurve, make a child of the image to ensure the two are always
# aligned.
#curve = scene.visuals.Isocurve(img_data, levels=levels, color_lev=color_lev,
#                              parent=view.scene, method='subdivide')

iso = Isoline(level=10, width=1., color='black')

canvas.title = 'Spatial Filtering using %s Filter' % interpolation

# Set 2D camera (the camera will scale to the contents in the scene)
view.camera = scene.PanZoomCamera(aspect=1)
# flip y-axis to have correct aligment
view.camera.flip = (0, 1, 0)
view.camera.set_range()

# get interpolation functions from Image
names = image.interpolation_functions
names = list(names)
names.sort()
print(names)
act = 17

act = -1

level = 2
first = True


# Implement key presses
@canvas.events.key_press.connect
def on_key_press(event):
    global act, level, first, interpolation
    if event.key in ['Left', 'Right']:
        if event.key == 'Right':
            step = 1
        else:
            step = -1
        act = (act + step) % len(names)
        interpolation = names[act]
        image.interpolation = interpolation

    if event.key in ['Up', 'Down']:
        if first:
            image.attach(iso)
            first = False
        if event.key == 'Up':
            level += 1
        else:
            if level > 1:
                level -= 1
        #levels = np.linspace(img_data.min(), img_data.max(), num=level+1, endpoint=True)[1:-1]
        #curve.levels = levels
        iso.level = level
    canvas.title = 'Spatial Filtering using %s Filter - Isoline %d level' % (interpolation, level)
    canvas.update()


if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()