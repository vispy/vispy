# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Texture Filter on Meshes
========================

Show how to use the texture filter on meshes.
"""

import argparse

import numpy as np
from vispy import app, scene
from vispy.io import imread, load_data_file, read_mesh
from vispy.scene.visuals import Mesh
from vispy.scene import transforms
from vispy.visuals.filters import TextureFilter


parser = argparse.ArgumentParser()
parser.add_argument('--shading', default='smooth',
                    choices=['none', 'flat', 'smooth'],
                    help="shading mode")
args, _ = parser.parse_known_args()

mesh_path = load_data_file('spot/spot.obj.gz')
texture_path = load_data_file('spot/spot.png')
vertices, faces, normals, texcoords = read_mesh(mesh_path)
texture = np.flipud(imread(texture_path))

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white',
                           size=(800, 600))
view = canvas.central_widget.add_view()

view.camera = 'arcball'
# Adapt the depth to the scale of the mesh to avoid rendering artefacts.
view.camera.depth_value = 10 * (vertices.max() - vertices.min())

shading = None if args.shading == 'none' else args.shading
mesh = Mesh(vertices, faces, shading=shading, color='white')
mesh.transform = transforms.MatrixTransform()
mesh.transform.rotate(90, (1, 0, 0))
mesh.transform.rotate(135, (0, 0, 1))
mesh.shading_filter.shininess = 1e+1
view.add(mesh)

texture_filter = TextureFilter(texture, texcoords)
mesh.attach(texture_filter)


@canvas.events.key_press.connect
def on_key_press(event):
    if event.key == "t":
        texture_filter.enabled = not texture_filter.enabled
        mesh.update()


def attach_headlight(mesh, view, canvas):
    light_dir = (0, 1, 0, 0)
    mesh.shading_filter.light_dir = light_dir[:3]
    initial_light_dir = view.camera.transform.imap(light_dir)

    @view.scene.transform.changed.connect
    def on_transform_change(event):
        transform = view.camera.transform
        mesh.shading_filter.light_dir = transform.map(initial_light_dir)[:3]


attach_headlight(mesh, view, canvas)


canvas.show()


if __name__ == "__main__":
    app.run()
