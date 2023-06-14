# -*- coding: utf-8 -*- 
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import numpy as np

from vispy.geometry import create_plane
from vispy.scene.visuals import Mesh
from vispy.testing import TestingCanvas
from vispy.visuals.filters import FacePickingFilter


def test_empty_mesh_face_picking():
    mesh = Mesh()
    filter = FacePickingFilter()
    mesh.attach(filter)
    filter.enabled = True


def test_face_picking():
    vertices, faces, _ = create_plane(125, 125)
    vertices = vertices["position"]
    vertices[:, :2] += 125 / 2
    mesh = Mesh(vertices=vertices, faces=faces)
    filter = FacePickingFilter()
    mesh.attach(filter)

    with TestingCanvas(size=(125, 125)) as c:
        view = c.central_widget.add_view()
        view.add(mesh)
        filter.enabled = True
        mesh.update_gl_state(blend=False)
        picking_render = c.render(bgcolor=(0, 0, 0, 0), alpha=True)

    # the plane is made up of two triangles and nearly fills the view
    # pick one point on each triangle
    assert np.allclose(
        picking_render[125 // 2, 125 // 4],
        (1, 0, 0, 0),
    )
    assert np.allclose(
        picking_render[125 // 2, 3 * 125 // 4],
        (2, 0, 0, 0),
    )
