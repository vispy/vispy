# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Picking Faces from a Mesh
=========================

Demonstrates how to identify (pick) individual faces on a mesh.

Arguments:
* --mesh - Path to a mesh file (OBJ/OBJ.GZ) [optional]

Controls:
* s  - Cycle shading modes (None, 'flat', 'smooth')
* w  - Toggle wireframe
* p  - Toggle face picking view - shows the colors encoding face ID
* c  - Clear painted faces
"""
import argparse
import itertools

import numpy as np

from vispy import app, scene
from vispy.io import read_mesh, load_data_file
from vispy.scene.visuals import Mesh
from vispy.scene import transforms
from vispy.visuals.filters import ShadingFilter, WireframeFilter, FacePickingFilter


parser = argparse.ArgumentParser()
default_mesh = load_data_file('orig/triceratops.obj.gz')
parser.add_argument('--mesh', default=default_mesh)
args, _ = parser.parse_known_args()

vertices, faces, _normals, _texcoords = read_mesh(args.mesh)

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white')
view = canvas.central_widget.add_view()

view.camera = 'arcball'
view.camera.depth_value = 1e3

# Create a colored `MeshVisual`.
face_colors = np.tile((0.5, 0.0, 0.5, 1.0), (len(faces), 1))
mesh = Mesh(
    vertices,
    faces,
    face_colors=face_colors.copy()
)
mesh.transform = transforms.MatrixTransform()
mesh.transform.rotate(90, (1, 0, 0))
mesh.transform.rotate(-45, (0, 0, 1))
view.add(mesh)

# Use filters to affect the rendering of the mesh.
wireframe_filter = WireframeFilter()
shading_filter = ShadingFilter()
face_picking_filter = FacePickingFilter()
mesh.attach(wireframe_filter)
mesh.attach(shading_filter)
mesh.attach(face_picking_filter)


def attach_headlight(view):
    light_dir = (0, 1, 0, 0)
    shading_filter.light_dir = light_dir[:3]
    initial_light_dir = view.camera.transform.imap(light_dir)

    @view.scene.transform.changed.connect
    def on_transform_change(event):
        transform = view.camera.transform
        shading_filter.light_dir = transform.map(initial_light_dir)[:3]


attach_headlight(view)

shading = itertools.cycle(("flat", "smooth", None))
shading_filter.shading = next(shading)


@canvas.events.mouse_move.connect
def on_mouse_move(event):
    restore_state = not face_picking_filter.enabled

    face_picking_filter.enabled = True
    mesh.update_gl_state(blend=False)
    picking_render = canvas.render(bgcolor=(0, 0, 0, 0), alpha=True)

    if restore_state:
        face_picking_filter.enabled = False

    mesh.update_gl_state(blend=not face_picking_filter.enabled)

    ids = picking_render.view(np.uint32) - 1
    # account for hidpi screens - canvas and render may have different size
    cols, rows = canvas.size
    col, row = event.pos
    col = int(col / cols * (ids.shape[1] - 1))
    row = int(row / rows * (ids.shape[0] - 1))

    # color the hovered face on the mesh
    if ids[row, col] in range(1, len(face_colors)):
        # this may be less safe, but it's faster
        mesh.mesh_data._face_colors_indexed_by_faces[ids[row, col]] = (0, 1, 0, 1)
        mesh.mesh_data_changed()


@canvas.events.key_press.connect
def on_key_press(event):
    if event.key == 'c':
        mesh.set_data(vertices, faces, face_colors=face_colors)
    if event.key == 's':
        shading_filter.shading = next(shading)
        mesh.update()
    elif event.key == 'w':
        wireframe_filter.enabled = not wireframe_filter.enabled
        mesh.update()
    elif event.key == 'p':
        # toggle face picking view
        face_picking_filter.enabled = not face_picking_filter.enabled
        mesh.update_gl_state(blend=not face_picking_filter.enabled)
        mesh.update()


canvas.show()


if __name__ == "__main__":
    print(__doc__)
    app.run()
