# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Display Mesh Normals
====================

Show how to display mesh normals on a mesh.
"""

from vispy import app, scene
from vispy.io import read_mesh, load_data_file
from vispy.scene.visuals import Mesh, MeshNormals
from vispy.visuals.filters import WireframeFilter


mesh_file = load_data_file('orig/triceratops.obj.gz')
vertices, faces, _, _ = read_mesh(mesh_file)

mesh = Mesh(vertices, faces, shading='flat')
meshdata = mesh.mesh_data

wireframe_filter = WireframeFilter(color='lightblue')
mesh.attach(wireframe_filter)

face_normals = MeshNormals(meshdata, primitive='face', color='yellow')
vertex_normals = MeshNormals(meshdata, primitive='vertex', color='orange',
                             width=2)

canvas = scene.SceneCanvas(keys='interactive', bgcolor='white')
view = canvas.central_widget.add_view()
view.camera = 'arcball'
view.add(mesh)
face_normals.parent = mesh
vertex_normals.parent = mesh


@canvas.events.key_press.connect
def on_key_press(event):
    if event.key == 'f':
        face_normals.visible = not face_normals.visible
        canvas.update()
    elif event.key == 'v':
        vertex_normals.visible = not vertex_normals.visible
        canvas.update()


canvas.show()


if __name__ == "__main__":
    print('Key bindings:')
    print(' f : toggle face normals')
    print(' v : toggle vertex normals')
    app.run()
