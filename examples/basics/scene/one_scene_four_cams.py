# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2

"""
Demonstrating a single scene that is shown in four different viewboxes,
each with a different camera.
"""

from vispy import app, scene, io

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()

# Create two ViewBoxes, place side-by-side
vb1 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)
vb2 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)
vb3 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)
vb4 = scene.widgets.ViewBox(border_color='white', parent=canvas.scene)
scenes = vb1.scene, vb2.scene, vb3.scene, vb4.scene


# Move these when the canvas changes size
@canvas.events.resize.connect
def resize(event=None):
    d = 5
    vb1.pos = d, d
    vb2.pos = canvas.size[0]/2 + d, d
    vb3.pos = d, canvas.size[1]/2. + d
    vb4.pos = canvas.size[0]/2 + d, canvas.size[1]/2. + d
    for vb in (vb1, vb2, vb3, vb4):
        vb.size = canvas.size[0]/2. - 2*d, canvas.size[1]/2. - 2*d

resize()

# Create some visuals to show
im1 = io.load_crate().astype('float32') / 255
image1 = scene.visuals.Image(im1, parent=scenes)

#vol1 = np.load(io.load_data_file('volume/stent.npz'))['arr_0']
#volume1 = scene.visuals.Volume(vol1, parent=scenes)
#volume1.transform = scene.STTransform(translate=(0, 0, 10))

# Assign cameras
vb1.camera = 'base'
vb2.camera = 'panzoom'
vb3.camera = 'turntable'
vb4.camera = 'fly'

# If True, show a cuboid at each camera
if False:
    cube = scene.visuals.Cube((3, 3, 5))
    cube.transform = scene.STTransform(translate=(0, 0, 6))
    for vb in (vb1, vb2, vb3, vb4):
        vb.camera.parents = scenes
        cube.add_parent(vb.camera)

if __name__ == '__main__':
    app.run()
