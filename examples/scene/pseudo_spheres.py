"""
Create a PseudoSpheres Visual
"""
import numpy as np
from vispy import app, scene

# Create canvas and view
canvas = scene.SceneCanvas(keys='interactive', size=(600, 600), show=True)
view = canvas.central_widget.add_view()
view.camera = scene.cameras.ArcballCamera(fov=0)
view.camera.scale_factor = 70

# Prepare data
np.random.seed(57983)
data = np.random.normal(size=(40, 3), loc=0, scale=10)
size = len(data) * [3]

data = np.concatenate([data, [[0, 0, 0]]], axis=0)
size.append(6)

colors = np.random.rand(41, 3)

# Create and show visual
vis = scene.visuals.PseudoSpheres(pos=data, size=size, color=colors)
vis.parent = view.scene
vis2 = scene.visuals.Markers(pos=data, size=size, face_color=colors)

# Run example
app.run()
