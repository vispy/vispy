# -*- coding: utf-8 -*-
# vispy: gallery 2
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""Render transparent objects with approximate order-independent transparency.

Using the method:

    McGuire, Morgan, and Louis Bavoil. "Weighted blended order-independent
    transparency." Journal of Computer Graphics Techniques 2.4 (2013).
"""

from vispy import app, scene
from vispy.io import read_mesh, load_data_file
from vispy.scene.visuals import Mesh, Plane
from vispy.visuals import transforms


mesh_file = load_data_file('orig/triceratops.obj.gz')
vertices, faces, _, _ = read_mesh(mesh_file)
center = vertices.mean(axis=0)
vertices = [
    vertices,
    (vertices - center) * 0.66 + center,
    vertices + [[0, 0, 0.75]],
    vertices + [[0, 0, 1.50]],
    vertices + [[0, 0, 2.25]],
]
scale = 1
vertices = [scale * v for v in vertices]

# shading = None
# shading = 'flat'
shading = 'smooth'
meshes = [
    Mesh(vertices[0], faces, shading=shading, color=(.2, .2, .5, .25)),
    Mesh(vertices[1], faces, shading=shading, color=(.2, .5, .5, .25)),
    Mesh(vertices[2], faces, shading=shading, color=(.2, .5, .2, .25)),
    Mesh(vertices[3], faces, shading=shading, color=(.5, .2, .2, .25)),
    Mesh(vertices[4], faces, shading=shading, color=(.5, .5, .2, 1)),
]

c = 0
d = 1
a = .25
planes = [
    Plane(color=(d, c, c, a)),
    Plane(color=(c, d, c, a)),
    Plane(color=(c, c, d, a)),
    Plane(color=(c, d, d, 1)),
]
for plane in planes:
    plane._mesh.shading = shading
positions = [
    (2, 0, 0.0),
    (2, 0, 0.75),
    (2, 0, 1.5),
    (2, .25, 2.25),
]
for plane, position in zip(planes, positions):
    plane.transform = transforms.STTransform(translate=position)
meshes += planes

bgcolor = 'white'
canvas = scene.SceneCanvas(keys='interactive', bgcolor=bgcolor)
view = canvas.central_widget.add_view()
view.camera = 'arcball'
view.camera.depth_value = 1e3
for mesh in meshes:
    view.add(mesh)

canvas.show()


if __name__ == "__main__":
    app.run()
