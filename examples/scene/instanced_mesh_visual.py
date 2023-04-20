# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Instanced Mesh Visual
=====================

Show usage of the InstancedMesh visual and its filters.
"""

from itertools import cycle

import numpy as np
from scipy.spatial.transform import Rotation
from vispy import app, scene, use
from vispy.io import imread, load_data_file, read_mesh
from vispy.scene.visuals import InstancedMesh
from vispy.visuals.filters import InstancedShadingFilter, WireframeFilter, TextureFilter

# needed for instanced rendering to work
use(gl='gl+')


mesh_path = load_data_file('spot/spot.obj.gz')
texture_path = load_data_file('spot/spot.png')
vertices, faces, normals, texcoords = read_mesh(mesh_path)
texture = np.flipud(imread(texture_path))

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white', show=True)
view = canvas.central_widget.add_view()

view.camera = 'arcball'
view.camera.depth_value = 10 * (vertices.max() - vertices.min())

n_instances = 100

instance_colors = np.random.rand(n_instances, 3).astype(np.float32)
instance_positions = ((np.random.rand(n_instances, 3) - 0.5) * 10).astype(np.float32)
face_colors = np.random.rand(len(faces), 3)
instance_transforms = Rotation.random(n_instances).as_matrix().astype(np.float32)

# Create a colored `MeshVisual`.
mesh = InstancedMesh(
    vertices,
    faces,
    instance_colors=instance_colors,
    face_colors=face_colors,
    instance_positions=instance_positions,
    instance_transforms=instance_transforms,
    parent=view.scene,
)


wireframe_filter = WireframeFilter(width=1)
shading_filter = InstancedShadingFilter('smooth', shininess=1)
texture_filter = TextureFilter(texture, texcoords)
mesh.attach(wireframe_filter)
mesh.attach(shading_filter)
mesh.attach(texture_filter)


def attach_headlight(view):
    light_dir = (0, 1, 0, 0)
    shading_filter.light_dir = light_dir[:3]
    initial_light_dir = view.camera.transform.imap(light_dir)

    @view.scene.transform.changed.connect
    def on_transform_change(event):
        transform = view.camera.transform
        shading_filter.light_dir = transform.map(initial_light_dir)[:3]


attach_headlight(view)


shading_cycle = cycle(['flat', None, 'smooth'])
color_cycle = cycle([None, instance_colors])
face_color_cycle = cycle([None, face_colors])


@canvas.events.key_press.connect
def on_key_press(event):
    if event.key == "t":
        texture_filter.enabled = not texture_filter.enabled
        canvas.update()
    if event.key == 's':
        shading_filter.shading = next(shading_cycle)
        canvas.update()
    if event.key == 'c':
        mesh.instance_colors = next(color_cycle)
        canvas.update()
    if event.key == 'f':
        mesh.set_data(
            vertices=vertices,
            faces=faces,
            face_colors=next(face_color_cycle),
        )
        canvas.update()
    if event.key == 'w':
        wireframe_filter.enabled = not wireframe_filter.enabled
        canvas.update()


if __name__ == "__main__":
    app.run()
