"""
Test automatic layout of multiple viewboxes using Grid.


"""
from vispy import scene
from vispy import app
import numpy as np

canvas = scene.SceneCanvas(close_keys='escape')
canvas.size = 600, 600
canvas.show()

grid = scene.widgets.Grid(canvas.scene)

# Ensure that grid fills the entire canvas, even after resize.
@canvas.events.resize.connect
def update_grid(event=None):
    global grid, canvas
    grid.size = canvas.size
    print(canvas.size)

update_grid()

b1 = grid.add_view(row=0, col=0, col_span=2)
b1.scene.camera = scene.cameras.TwoDCamera()
b1.border = (1, 0, 0, 1)
b1.preferred_clip_method = 'viewport'

b2 = grid.add_view(row=1, col=0)
b2.scene.camera = scene.cameras.TwoDCamera()
b2.border = (1, 0, 0, 1)
b2.preferred_clip_method = 'viewport'

b3 = grid.add_view(row=1, col=1)
b3.scene.camera = scene.cameras.TwoDCamera()
b3.border = (1, 0, 0, 1)
b3.preferred_clip_method = 'viewport'


# Add one line to all three boxes
N = 10000
pos = np.empty((N, 2), dtype=np.float32)
pos[:, 0] = np.linspace(0, 10, N)
pos[:, 1] = np.random.normal(size=N)
#
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

l1 = scene.visuals.Line(pos=pos, color=color)
#l1.transform = scene.transforms.AffineTransform()
#l1.transform.scale((10, 1))
#l1.transform.translate((20, 100))

b1.add(l1)
b2.add(l1)
b3.add(l1)


# add image to b1
#img_data = np.random.normal(size=(100, 100, 3), loc=128,
                            #scale=50).astype(np.ubyte)

#image = scene.visuals.Image(img_data)
#image.transform = scene.transforms.AffineTransform()
#image.transform.scale((1, 1))
#b1.add(image)

import sys
if sys.flags.interactive == 0:
    app.run()
