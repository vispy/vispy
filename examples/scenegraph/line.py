"""
Simple test of SceneCanvas containing a single line entity
as its entire scenegraph.
"""
from vispy import scenegraph
from vispy import app
from vispy.visuals import transforms
import numpy as np

canvas = scenegraph.SceneCanvas()
canvas.size = 800, 600
canvas.show()

N = 1000
pos = np.empty((N,2), np.float32)
pos[:,0] = np.linspace(0., 1., N)
pos[:,1] = np.random.normal(size=N)
#
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

line = scenegraph.entities.Line(parents=[canvas.root], pos=pos, color=color)
line.transform.scale((700, 50))
line.transform.translate((50, 300))

app.run()
