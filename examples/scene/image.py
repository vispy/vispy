"""
Simple test of SceneCanvas containing a single line entity
as its entire scenegraph.
"""
from vispy import scene
from vispy import app
import numpy as np

canvas = scene.SceneCanvas(close_keys='escape')
canvas.size = 800, 600
canvas.show()

img_data = np.random.normal(size=(100, 100, 3), loc=128,
                            scale=50).astype(np.ubyte)

image = scene.visuals.Image(canvas.scene, img_data)
image.transform = scene.transforms.STTransform(translate=(100, 100))

# todo: where is the image?

app.run()
