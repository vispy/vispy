# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import numpy as np

from vispy.geometry import create_plane
from vispy.scene.visuals import Markers, Mesh
from vispy.testing import requires_application, TestingCanvas
from vispy.visuals.filters import FacePickingFilter, MarkerPickingFilter


def test_empty_mesh_face_picking():
    mesh = Mesh()
    filter = FacePickingFilter()
    mesh.attach(filter)
    filter.enabled = True


@requires_application()
def test_mesh_face_picking():
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

    # unpack the IDs
    ids = picking_render.view(np.uint32)
    # the plane is made up of two triangles and nearly fills the view
    # pick one point on each triangle
    assert ids[125 // 2, 125 // 4] == 1
    assert ids[125 // 2, 3 * 125 // 4] == 2


def test_empty_markers_picking():
    markers = Markers()
    filter = MarkerPickingFilter()
    markers.attach(filter)
    filter.enabled = True


@requires_application()
def test_markers_picking():
    markers = Markers(
        pos=np.array([[-0.5, -0.5], [0.5, 0.5]]),
        size=5,
    )
    filter = MarkerPickingFilter()
    markers.attach(filter)

    with TestingCanvas(size=(125, 125)) as c:
        view = c.central_widget.add_view(camera="panzoom")
        view.camera.rect = (-1, -1, 2, 2)
        view.add(markers)

        filter.enabled = True
        markers.update_gl_state(blend=False)
        picking_render = c.render(bgcolor=(0, 0, 0, 0), alpha=True)
        ids = picking_render.view(np.uint32)

        assert ids[3 * 125 // 4, 125 // 4] == 1
        assert ids[125 // 4, 3 * 125 // 4] == 2
