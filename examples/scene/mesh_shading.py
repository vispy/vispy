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
import argparse
import time

import numpy as np

from vispy import app, scene
from vispy.geometry import MeshData
from vispy.io import read_mesh, load_data_file
from vispy.scene.visuals import Mesh
from vispy.scene import transforms
from vispy.visuals.filters import ShadingFilter, WireframeFilter


parser = argparse.ArgumentParser()
default_mesh = load_data_file('orig/triceratops.obj.gz')
parser.add_argument('--mesh', default=default_mesh)
parser.add_argument('--shininess', default=100)
parser.add_argument('--wireframe-width', default=1)
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
    # color=(0.5, 0.0, 0.5, 1.0)
    face_colors=face_colors
)
mesh.transform = transforms.MatrixTransform()
mesh.transform.rotate(90, (1, 0, 0))
mesh.transform.rotate(-45, (0, 0, 1))
view.add(mesh)

colors = np.arange(1, len(faces) + 1, dtype=np.uint32).view(np.uint8).reshape(len(faces), 4) / 255
picking_mesh = Mesh(
    meshdata=MeshData(
        mesh.mesh_data.get_vertices(),
        mesh.mesh_data.get_faces(),
        face_colors=colors,
    )
)
picking_mesh.transform = mesh.transform
picking_mesh.update_gl_state(depth_test=True, blend=False)
picking_mesh.visible = False
view.add(picking_mesh)

# Use filters to affect the rendering of the mesh.
wireframe_filter = WireframeFilter(width=args.wireframe_width)
# Note: For convenience, this `ShadingFilter` would be created automatically by
# the `MeshVisual with, e.g. `mesh = MeshVisual(..., shading='smooth')`. It is
# created manually here for demonstration purposes.
shading_filter = ShadingFilter(shininess=args.shininess)
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

shading_states = (
    dict(shading=None),
    dict(shading='flat'),
    dict(shading='smooth'),
)
shading_state_index = shading_states.index(
    dict(shading=shading_filter.shading))

wireframe_states = (
    dict(wireframe_only=False, faces_only=False,),
    dict(wireframe_only=True, faces_only=False,),
    dict(wireframe_only=False, faces_only=True,),
)
wireframe_state_index = wireframe_states.index(dict(
    wireframe_only=wireframe_filter.wireframe_only,
    faces_only=wireframe_filter.faces_only,
))


def cycle_state(states, index):
    new_index = (index + 1) % len(states)
    return states[new_index], new_index


camera_moving = False


@canvas.events.mouse_press.connect
def on_mouse_press(event):
    global camera_moving
    camera_moving = True


@canvas.events.mouse_release.connect
def on_mouse_release(event):
    global camera_moving
    camera_moving = False


@canvas.events.mouse_move.connect
def on_mouse_move(event):
    with canvas.events.mouse_move.blocker():
        start = time.perf_counter()
        readd_mesh = False
        if mesh.visible:
            mesh.visible = False
            readd_mesh = True
        picking_mesh.visible = True
        picking_mesh.update_gl_state(depth_test=True, blend=False)
        # if mesh.parent is not None:
        #     readd_mesh = True
        #     mesh.parent = None
        # if picking_mesh.parent is None:
        #     picking_mesh.update_gl_state(depth_test=True, blend=False)
        #     view.add(picking_mesh)
        # print("switch to picking visual", time.perf_counter() - start)

        start = time.perf_counter()
        picking_render = canvas.render(bgcolor=(0, 0, 0, 0), alpha=True)
        col, row = event.pos
        # TODO: handle hidpi screens properly
        # col *= 2
        # row *= 2
        # print(col, row, picking_render.shape)
        id = picking_render.view(np.uint32) - 1
        # print("do picking", time.perf_counter() - start)

        start = time.perf_counter()
        if readd_mesh:
            mesh.visible = True
            picking_mesh.visible = False
            # picking_mesh.parent = None
            # view.add(mesh)

        meshdata = mesh.mesh_data
        if id[row, col] > 0 and id[row, col] < len(face_colors):
            face_colors[id[row, col], :] = (0, 1, 0, 1)
            # meshdata.set_face_colors(face_colors)
            # mesh.set_data(meshdata=meshdata)
            # this is unsafe but faster
            meshdata._face_colors_indexed_by_faces[id[row, col]] = (0, 1, 0, 1)
            mesh.mesh_data_changed()
        # print("switch back", time.perf_counter() - start)


@canvas.events.key_press.connect
def on_key_press(event):
    global shading_state_index
    global wireframe_state_index
    if event.key == 's':
        state, shading_state_index = cycle_state(shading_states,
                                                 shading_state_index)
        for attr, value in state.items():
            setattr(shading_filter, attr, value)
        mesh.update()
    elif event.key == 'w':
        wireframe_filter.enabled = not wireframe_filter.enabled
        mesh.update()
    elif event.key == 'p':
        if mesh.visible:
            picking_mesh.visible = True
            mesh.visible = False
            view.bgcolor = (0, 0, 0, 1)
        elif picking_mesh.visible:
            picking_mesh.visible = False
            mesh.visible = True
            view.bgcolor = (1, 1, 1, 1)
        # if picking_mesh.parent is None:
        #     mesh.parent = None
        #     view.bgcolor = (0, 0, 0, 1)
        #     view.add(picking_mesh)
        # else:
        #     picking_mesh.parent = None
        #     view.bgcolor = (1, 1, 1, 1)
        #     view.add(mesh)


canvas.show()


if __name__ == "__main__":
    app.run()
