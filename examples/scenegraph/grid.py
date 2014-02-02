"""
Simple test of SceneCanvas containing a single line entity
as its entire scenegraph.
"""
from vispy import scenegraph
from vispy import app
from vispy.visuals import transforms
import numpy as np

canvas = scenegraph.SceneCanvas()
canvas.size = 600, 600
canvas.show()

#pos = np.empty((1000,2))
#pos[:,0] = np.linspace(-0.9, 0.9, 1000)
#pos[:,1] = np.random.normal(size=1000)

grid = scenegraph.entities.GridBox(parent=canvas.root, border=(1, 0, 0, 1))

grid.add_box(row=0, col=0)
grid.add_box(row=0, col=1)
grid.add_box(row=1, col=0)
grid.add_box(row=1, col=1)

app.run()
