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

img_data = np.random.normal(size=(100, 100, 3), loc=128, scale=50).astype(np.ubyte)

image = scenegraph.entities.Image(img_data, parents=[canvas.root])
image.transform.translate((100, 100))

app.run()
