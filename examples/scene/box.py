"""
Simple test of SceneCanvas containing a single line entity
as its entire scenegraph.
"""
from vispy import scene
from vispy import app
import numpy as np

canvas = scene.SceneCanvas(close_keys='escape')
canvas.size = 600, 600
canvas.show()

# ? the pos is not used?
pos = np.empty((1000, 2))
pos[:, 0] = np.linspace(-0.9, 0.9, 1000)
pos[:, 1] = np.random.normal(size=1000)

box = scene.widgets.Widget(canvas.scene)

app.run()
