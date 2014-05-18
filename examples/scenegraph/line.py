"""
Simple test of SceneCanvas containing a single line entity
as its entire scenegraph.
"""
import numpy as np

from vispy import app
from vispy import scene

canvas = scene.SceneCanvas(size=(800,600), show=True)

N = 1000
pos = np.empty((N,2), np.float32)
pos[:,0] = np.linspace(0., 1., N)
pos[:,1] = np.random.normal(size=N)
#
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

line = scene.visuals.Line(parents=canvas.root, pos=pos, color=color)
line.transform = scene.transforms.STTransform(scale=(700, 50))
# line.transform.scale = 700, 50
line.transform.translate = 50, -300
canvas.root.camera = scene.cameras.PixelCamera()

app.run()
