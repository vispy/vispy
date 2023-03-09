# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Shading a Mesh
==============

Show mesh filter usage for shading (lighting) a mesh and displaying a wireframe.
"""

import numpy as np
from scipy.spatial.transform import Rotation
from vispy import app, scene, use
from vispy.io import read_mesh, load_data_file
from vispy.scene.visuals import InstancedMesh
from vispy.visuals.filters import ShadingFilter, WireframeFilter

# needed for instanced rendering to work
use(gl='gl+')


triceratops = load_data_file('orig/triceratops.obj.gz')
vertices, faces, normals, texcoords = read_mesh(triceratops)

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white', show=True)
view = canvas.central_widget.add_view()

view.camera = 'arcball'
view.camera.depth_value = 1e3

n_instances = 100
# Create a colored `MeshVisual`.
mesh = InstancedMesh(
    vertices,
    faces,
    instance_colors=np.random.rand(n_instances, 3),
    instance_positions=(np.random.rand(n_instances, 3) - 0.5) * 10,
    instance_transforms=Rotation.random(n_instances).as_matrix(),
    parent=view.scene,
)

wireframe_filter = WireframeFilter(width=1)
shading_filter = ShadingFilter('smooth', shininess=100)
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


if __name__ == "__main__":
    app.run()
