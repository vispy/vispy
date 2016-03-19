# pyline: disable=no-member
""" plot3d using existing visuals : LinePlotVisual """

import numpy as np
from vispy import app, visuals, scene

# build visuals
Plot3D = scene.visuals.create_visual_node(visuals.LinePlotVisual)

# build canvas
canvas = scene.SceneCanvas(keys='interactive', show=True)

# Add a ViewBox to let the user zoom/rotate
view = canvas.central_widget.add_view()
view.camera = 'turntable'
view.camera.fov = 45
view.camera.distance = 6

# prepare data
N = 60
x = np.sin(np.linspace(-2, 2, N)*np.pi)
y = np.cos(np.linspace(-2, 2, N)*np.pi)
z = np.linspace(-2, 2, N)

# plot
pos = np.c_[x, y, z]
p1 = Plot3D(pos, width=2.0, color='red',
            edge_color='w', symbol='o', face_color=(0.2, 0.2, 1, 0.8),
            parent=view.scene)

# run
app.run()
