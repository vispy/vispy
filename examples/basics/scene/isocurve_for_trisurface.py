# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""
This example demonstrates isocurve for triangular mesh with vertice data.
"""

import numpy as np

from vispy import app, scene

from vispy.geometry.generation import create_sphere

import sys

# Create a canvas with a 3D viewport
canvas = scene.SceneCanvas(keys='interactive')
canvas.show()
view = canvas.central_widget.add_view()
view.set_camera('turntable', mode='perspective', up='z', distance=5)

cols = 10
rows = 10
radius = 2
nbr_level = 20
mesh = create_sphere(cols, rows, radius=radius)
vertices = mesh.get_vertices()
tris = mesh.get_faces()

cl = np.linspace(-radius, radius, nbr_level+2)[1:-1]

scene.visuals.Isoline(vertices=vertices, tris=tris, data=vertices[:, 2],
                      level=cl, color_lev='autumn', parent=view.scene)

# Add a 3D axis to keep us oriented
scene.visuals.XYZAxis(parent=view.scene)


if __name__ == '__main__':
    canvas.show()
    if sys.flags.interactive == 0:
        app.run()
