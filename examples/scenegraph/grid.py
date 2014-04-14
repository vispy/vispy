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

grid = canvas.root.add_grid()

b1 = grid.add_view(row=0, col=0, col_span=2)
b2 = grid.add_view(row=1, col=0)
b3 = grid.add_view(row=1, col=1)


# Add one line to all three boxes
N = 10000
pos = np.empty((N,2), dtype=np.float32)
pos[:,0] = np.linspace(0, 10, N)
pos[:,1] = np.random.normal(size=N)
#
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

l1 = scenegraph.entities.Line(pos, color=color)
l1.transform.scale((10, 1))
l1.transform.translate((20, 100))

b1.add(l1)
b2.add(l1)
b3.add(l1)


# add image to b1
img_data = np.random.normal(size=(100, 100, 3), loc=128, scale=50).astype(np.ubyte)

image = scenegraph.entities.Image(img_data)
image.transform.scale((1, 1))
b1.add(image)

import sys
if sys.flags.interactive == 0:
    app.run()
