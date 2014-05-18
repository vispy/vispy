"""
Simple test of stacking viewboxes.
"""

import sys
import numpy as np

from vispy import app, gloo
from vispy import scene

gloo.gl.use('desktop debug')

canvas = scene.SceneCanvas(size=(800,600), show=True)

# Create line x:0..1 y: random numbers with std 1
N = 1000
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]
pos = np.empty((N,2), np.float32)
#
pos[:,0] = np.linspace(-1., 1., N)
pos[:,1] = np.random.normal(0.0, 0.5, size=N)
line_ndc = scene.visuals.Line(pos=pos.copy(), color=color)
#
pos[:,0] = np.linspace(50, 350., N)
pos[:,1] = 150 + pos[:,1] * 50
line_pixels = scene.visuals.Line(pos=pos.copy(), color=color)

canvas.root.camera = scene.cameras.NDCCamera()  # Default NDCCamera


vb1 = scene.ViewBox(canvas.root)
vb1.pos = -1.0, -1.0
vb1.size = 1.0, 2.0
vb1.camera = scene.cameras.NDCCamera()
#
vb11 = scene.ViewBox(vb1)
vb11.pos = -1.0, -1.0
vb11.size = 2.0, 1.0
vb11.camera = scene.cameras.NDCCamera()
#
vb12 = scene.ViewBox(vb1)
vb12.pos = -1.0, 0.0
vb12.size = 2.0, 1.0
vb12.camera = scene.cameras.PixelCamera()
#
line_ndc.add_parent(vb11)
line_pixels.add_parent(vb12)


vb2 = scene.ViewBox(canvas.root)
vb2.pos = 0.0, -1.0
vb2.size = 1.0, 2.0
vb2.camera = scene.cameras.PixelCamera()
#
vb21 = scene.ViewBox(vb2)
vb21.pos = 0, 0
vb21.size = 400, 300
vb21.camera = scene.cameras.NDCCamera()
#
vb22 = scene.ViewBox(vb2)
vb22.pos = 0, 300
vb22.size = 400, 300
vb22.camera = scene.cameras.PixelCamera()
#
line_ndc.add_parent(vb21)
line_pixels.add_parent(vb22)


# Testing
vb1._name = 'vb1'
vb11._name = 'vb11'
vb12._name = 'vb12'
vb2._name = 'vb2'
vb21._name = 'vb21'
vb22._name = 'vb22'


if sys.flags.interactive == 0:
    app.run()
