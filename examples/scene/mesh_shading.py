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

from vispy import app, scene
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

vertices, faces, normals, texcoords = read_mesh(args.mesh)

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
    elif event.key == 'f':
        state, wireframe_state_index = cycle_state(wireframe_states,
                                                   wireframe_state_index)
        for attr, value in state.items():
            setattr(wireframe_filter, attr, value)
        mesh.update()


canvas.show()


if __name__ == "__main__":
    app.run()
