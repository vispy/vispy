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

pos = np.empty((1000,2))
pos[:,0] = np.linspace(0., 1., 1000)
pos[:,1] = np.random.normal(size=1000)

line = scenegraph.entities.Line(parents=[canvas.root], pos=pos)
line.transform.translate((50, 300))
line.transform.scale((700, 50))

app.run()
