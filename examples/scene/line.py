"""
Simple test of SceneCanvas containing a single line entity
as its entire scenegraph.
"""
import numpy as np

from vispy import app
from vispy import scene

canvas = scene.SceneCanvas(size=(800, 600), show=True, close_keys='escape')

N = 1000
pos = np.empty((N, 2), np.float32)
pos[:, 0] = np.linspace(0., 1., N)
pos[:, 1] = np.random.normal(0.5, 0.2, size=N)
#
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

line = scene.visuals.Line(canvas.scene, pos=pos, color=color)

# We need to either use a unit camera, or scale the line up 
# Uncomment ONE of the lines below
canvas.scene.camera = scene.cameras.UnitCamera()
#line.transform = scene.transforms.STTransform(scale=(400, 400))

app.run()
