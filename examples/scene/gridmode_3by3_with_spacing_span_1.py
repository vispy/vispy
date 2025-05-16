# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Grid of shape 3x3
=================

Demonstrate 3x3 grid that includes spacing between viewboxes but no span higher than 1.
"""
import sys
import numpy as np

from vispy import app
from vispy import scene


# Create canvas
canvas = scene.SceneCanvas(size=(800, 600), show=True, keys='interactive')
grid = canvas.central_widget.add_grid(spacing=(50,50))

# Create two ViewBoxes, place side-by-side
vb1 = grid.add_view(name='vb1', border_color='yellow', row=0, col=0)
# First ViewBox uses a 2D pan/zoom camera
vb1.camera = 'panzoom'

# Second ViewBox uses a 3D perspective camera
vb2 = grid.add_view(name='vb2', border_color='yellow', row=0, col=1)
vb2.parent = canvas.scene
vb2.camera = scene.TurntableCamera(elevation=30, azimuth=30, up='+y')

vb3 = grid.add_view(name='vb3', border_color='yellow', row=0, col=2)
vb3.parent = canvas.scene
vb3.camera = scene.TurntableCamera(elevation=30, azimuth=30, up='+y')

vb4 = grid.add_view(name='vb4', border_color='yellow',  row=1, col=0)
vb4.parent = canvas.scene
vb4.camera = scene.TurntableCamera(elevation=30, azimuth=30, up='+y')

vb5 = grid.add_view(name='vb5', border_color='yellow',  row=1, col=1)
vb5.parent = canvas.scene
vb5.camera = scene.TurntableCamera(elevation=30, azimuth=30, up='+y')

vb6 = grid.add_view(name='vb6', border_color='yellow',  row=1, col=2)
vb6.parent = canvas.scene
vb6.camera = scene.TurntableCamera(elevation=30, azimuth=30, up='+y')

vb7 = grid.add_view(name='vb7', border_color='yellow',  row=2, col=0)
vb7.parent = canvas.scene
vb7.camera = scene.TurntableCamera(elevation=30, azimuth=30, up='+y')

vb8 = grid.add_view(name='vb8', border_color='yellow',  row=2, col=1)
vb8.parent = canvas.scene
vb8.camera = scene.TurntableCamera(elevation=30, azimuth=30, up='+y')

vb9 = grid.add_view(name='vb9', border_color='yellow',  row=2, col=2)
vb9.parent = canvas.scene
vb9.camera = scene.TurntableCamera(elevation=30, azimuth=30, up='+y')
#
# Now add visuals to the viewboxes.
#

# First a plot line:
N = 1000
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

pos = np.empty((N, 2), np.float32)
pos[:, 0] = np.linspace(-1., 1., N)
pos[:, 1] = np.random.normal(0.0, 0.5, size=N)
pos[:20, 1] = -0.5  # So we can see which side is down

# make a single plot line and display in both viewboxes
line1 = scene.visuals.Line(pos=pos.copy(), color=color, method='gl',
                           antialias=False, name='line1', parent=vb1.scene)
line2 = scene.visuals.Line(pos=pos.copy(), color=color, method='gl',
                           antialias=False, name='line1', parent=vb2.scene)
line3 = scene.visuals.Line(pos=pos.copy(), color=color, method='gl',
                           antialias=False, name='line1', parent=vb3.scene)
line4 = scene.visuals.Line(pos=pos.copy(), color=color, method='gl',
                           antialias=False, name='line1', parent=vb4.scene)
line5 = scene.visuals.Line(pos=pos.copy(), color=color, method='gl',
                           antialias=False, name='line1', parent=vb5.scene)
line6 = scene.visuals.Line(pos=pos.copy(), color=color, method='gl',
                           antialias=False, name='line1', parent=vb6.scene)
line7 = scene.visuals.Line(pos=pos.copy(), color=color, method='gl',
                           antialias=False, name='line1', parent=vb7.scene)
line8 = scene.visuals.Line(pos=pos.copy(), color=color, method='gl',
                           antialias=False, name='line1', parent=vb8.scene)
line9 = scene.visuals.Line(pos=pos.copy(), color=color, method='gl',
                           antialias=False, name='line1', parent=vb9.scene)
# # And some squares:
box = np.array([[0, 0, 0],
                [0, 1, 0],
                [1, 1, 0],
                [1, 0, 0],
                [0, 0, 0]], dtype=np.float32)
z = np.array([[0, 0, 1]], dtype=np.float32)

# First two boxes are added to both views
box1 = scene.visuals.Line(pos=box, color=(0.7, 0, 0, 1), method='gl',
                          name='unit box', parent=vb1.scene)
box2 = scene.visuals.Line(pos=box, color=(0.7, 0, 0, 1), method='gl',
                          name='unit box', parent=vb2.scene)

box2 = scene.visuals.Line(pos=(box * 2 - 1), color=(0, 0.7, 0, 1),
                          method='gl', name='nd box', parent=vb1.scene)
box3 = scene.visuals.Line(pos=(box * 2 - 1), color=(0, 0.7, 0, 1),
                          method='gl', name='nd box', parent=vb2.scene)

# These boxes are only added to the 3D view.
box3 = scene.visuals.Line(pos=box + z, color=(1, 0, 0, 1),
                          method='gl', name='unit box', parent=vb2.scene)
box5 = scene.visuals.Line(pos=((box + z) * 2 - 1), color=(0, 1, 0, 1),
                          method='gl', name='nd box', parent=vb2.scene)


if __name__ == '__main__' and sys.flags.interactive == 0:
   # print(canvas.scene.describe_tree(with_transform=True))
    app.run()