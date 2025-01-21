# -*- coding: utf-8 -*-
# vispy: gallery 2
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Spheres and Sticks
==================

Draw spherical Markers with Tube meshes connecting them.
"""
import numpy as np
from vispy import app, scene

# Create canvas and view
canvas = scene.SceneCanvas(keys='interactive', size=(600, 600), show=True)
view = canvas.central_widget.add_view()
view.camera = scene.cameras.ArcballCamera(fov=0)
view.camera.scale_factor = 500

# Prepare data
np.random.seed(57983)
data = np.random.normal(size=(40, 3), loc=0, scale=100)
size = np.random.rand(40) * 100
colors = np.random.rand(40, 3)

data = np.concatenate([data, [[0, 0, 0]]], axis=0)
size = np.concatenate([size, [100]], axis=0)
colors = np.concatenate([colors, [[1, 0, 0]]], axis=0)


# Create and show visual
vis = scene.visuals.Markers(
    pos=data,
    size=100,
    antialias=0,
    face_color=colors,
    edge_color='white',
    edge_width=0,
    scaling=True,
    spherical=True,
)
vis.parent = view.scene

lines = np.array([[data[i], data[-1]]
                  for i in range(len(data) - 1)])
line_vis = []

for line in lines:
    vis2 = scene.visuals.Tube(line, radius=5)
    vis2.parent = view.scene
    line_vis.append(vis2)

if __name__ == "__main__":
    app.run()
