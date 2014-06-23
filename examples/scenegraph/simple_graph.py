"""
Simple Visual in two containers. This really helped me track down 
the bug in transforms.
"""

import sys
import numpy as np

from vispy import app, gloo
from vispy import scene

gloo.gl.use('desktop debug')


# Create lines for use in ndc and pixel coordinates
N = 1000
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]
pos = np.empty((N,2), np.float32)
#
pos[:,0] = np.linspace(-0.1, 0.1, N)
pos[:,1] = np.random.normal(0.0, 0.5, size=N)
pos[:20,1] = -0.5  # So we can see which side is down
line_ndc = scene.visuals.Line(pos=pos.copy(), color=color)

# Create canvas
canvas = scene.SceneCanvas(size=(800,600), show=True)
canvas.root.camera = scene.cameras.NDCCamera()  # Default NDCCamera

# Create a line in two containers
container1 = scene.Entity(canvas.root)
container2 = scene.Entity(container1)
line_ndc.add_parent(container2)

# 
container1.transform = scene.transforms.STTransform()
container2.transform = scene.transforms.STTransform()
line_ndc.transform = scene.transforms.STTransform()

if 1:
    container1.transform.scale = 2,1
    container2.transform.translate = 0.5, 0
    
else:
    line_ndc.transform.scale = 2,1
    line_ndc.transform.translate = 1, 0