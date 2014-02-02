"""
Simple test of SceneCanvas containing a single line entity
as its entire scenegraph.
"""
from vispy import scenegraph
from vispy import app
import numpy as np

# app.use('glut')

canvas = scenegraph.SceneCanvas()
canvas.size = 600, 600
canvas.show()

pos = np.array([
    [0, 0],
    [.5, 0],
    [.5, .5],
    [0, .5]])
line = scenegraph.entities.Line(pos=pos)
canvas.root_entity = line

app.run()
