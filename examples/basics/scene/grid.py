"""
Test automatic layout of multiple viewboxes using Grid.


"""
from vispy import scene
from vispy import app
import numpy as np

canvas = scene.SceneCanvas(close_keys='escape')
canvas.size = 600, 600
canvas.show()

grid = scene.widgets.Grid(parent=canvas.scene)


# Ensure that grid fills the entire canvas, even after resize.
@canvas.events.resize.connect
def update_grid(event=None):
    global grid, canvas
    grid.size = canvas.size

update_grid()

b1 = grid.add_view(row=0, col=0, col_span=2)
b1.border_color = (0.5, 0.5, 0.5, 1)
b1.camera.rect = (-0.5, -5), (11, 10)
b1.border = (1, 0, 0, 1)

b2 = grid.add_view(row=1, col=0)
b2.border_color = (0.5, 0.5, 0.5, 1)
b2.camera.rect = (-10, -5), (15, 10)
b2.border = (1, 0, 0, 1)

b3 = grid.add_view(row=1, col=1)
b3.border_color = (0.5, 0.5, 0.5, 1)
b3.camera.rect = (-5, -5), (10, 10)
b3.border = (1, 0, 0, 1)


# Add one line to all three boxes
N = 10000
pos = np.empty((N, 2), dtype=np.float32)
pos[:, 0] = np.linspace(0, 10, N)
pos[:, 1] = np.random.normal(size=N)
pos[5000, 1] += 50

color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

l1 = scene.visuals.Line(pos=pos, color=color)

b1.add(l1)

tr1 = scene.visuals.Visual()
tr1.transform = scene.transforms.LogTransform(base=(2, 0, 0))
l1.add_parent(tr1)
b2.add(tr1)

tr2 = scene.visuals.Visual()
tr2.transform = scene.transforms.PolarTransform()
l1.add_parent(tr2)
b3.add(tr2)

import sys
if sys.flags.interactive == 0:
    app.run()
