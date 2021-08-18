# -*- coding: utf-8 -*-
# vispy: gallery 10
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Interactively clip a Mesh with clipping planes
==============================================

Controls:
- x/y/z/o - add new clipping plane with normal along x/y/z or [1,1,1] oblique axis
- r - remove a clipping plane
"""

import numpy as np

from vispy import app, scene
from vispy.io import read_mesh, load_data_file
from vispy.scene.visuals import Mesh
from vispy.scene import transforms
from vispy.visuals.filters import ShadingFilter, WireframeFilter


default_mesh = load_data_file('orig/triceratops.obj.gz')

vertices, faces, normals, texcoords = read_mesh(default_mesh)

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white')
view = canvas.central_widget.add_view()

view.camera = 'arcball'
view.camera.depth_value = 1e3

# Create a colored `MeshVisual`.
mesh = Mesh(vertices, faces, color=(.5, .7, .5, 1))
mesh.transform = transforms.MatrixTransform()
mesh.transform.rotate(90, (1, 0, 0))
mesh.transform.rotate(-45, (0, 0, 1))
view.add(mesh)

# Use filters to affect the rendering of the mesh.
wireframe_filter = WireframeFilter(width=1)
# Note: For convenience, this `ShadingFilter` would be created automatically by
# the `MeshVisual with, e.g. `mesh = MeshVisual(..., shading='smooth')`. It is
# created manually here for demonstration purposes.
shading_filter = ShadingFilter(shininess=100)
# The wireframe filter is attached before the shading filter otherwise the
# wireframe is not shaded.
mesh.attach(wireframe_filter)
mesh.attach(shading_filter)


def attach_headlight(view):
    light_dir = (0, 1, 0, 0)
    shading_filter.light_dir = light_dir[:3]
    initial_light_dir = view.camera.transform.imap(light_dir)

    @view.scene.transform.changed.connect
    def on_transform_change(event):
        transform = view.camera.transform
        shading_filter.light_dir = transform.map(initial_light_dir)[:3]


attach_headlight(view)
canvas.show()

# clipping logic
points_center = [0, 0, 0]

clip_modes = {
    'x': np.array([[points_center, [0, 0, 1]]]),
    'y': np.array([[points_center, [0, 1, 0]]]),
    'z': np.array([[points_center, [1, 0, 0]]]),
    'o': np.array([[points_center, [1, 1, 1]]]),
}


def add_clip(mesh_visual, mode):
    if mode in clip_modes:
        new_plane = clip_modes[mode]
        if mesh_visual.clipping_planes is None:
            mesh_visual.clipping_planes = new_plane
        else:
            mesh_visual.clipping_planes = np.concatenate([mesh_visual.clipping_planes, new_plane])


def remove_clip(mesh_visual):
    if mesh_visual.clipping_planes is not None:
        mesh_visual.clipping_planes = mesh_visual.clipping_planes[:-1]


# Implement key presses
@canvas.events.key_press.connect
def on_key_press(event):
    if event.text in 'xyzo':
        add_clip(mesh, event.text)
    elif event.text == 'r':
        remove_clip(mesh)


if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        app.run()
