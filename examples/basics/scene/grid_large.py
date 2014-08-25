"""
Test automatic layout of multiple viewboxes using Grid.


"""
from vispy import scene
from vispy import app
import numpy as np

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 600, 600
canvas.show()

grid = scene.widgets.Grid(parent=canvas.scene)


# Ensure that grid fills the entire canvas, even after resize.
@canvas.events.resize.connect
def update_grid(event=None):
    global grid, canvas
    grid.size = canvas.size

update_grid()

N = 10000
lines = []
for i in range(10):
    lines.append([])
    for j in range(10):
        vb = grid.add_view(row=i, col=j)
        vb.camera.rect = (0, -5), (100, 10)
        vb.border = (1, 1, 1, 0.4)

        pos = np.empty((N, 2), dtype=np.float32)
        pos[:, 0] = np.linspace(0, 100, N)
        pos[:, 1] = np.random.normal(size=N)
        line = scene.visuals.Line(pos=pos, color=(1, 1, 1, 0.5), mode='gl')
        vb.add(line)


import sys
if sys.flags.interactive == 0:
    app.run()
