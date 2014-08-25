"""
Simple use of SceneCanvas to display an Image.
"""
from vispy import scene
from vispy import app
import numpy as np

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 800, 600
canvas.show()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Create the image
img_data = np.random.normal(size=(100, 100, 3), loc=128,
                            scale=50).astype(np.ubyte)
image = scene.visuals.Image(img_data, parent=view.scene)

# Set the view bounds to show the entire image with some padding
view.camera.rect = (-10, -10, image.size[0]+20, image.size[1]+20)

app.run()
