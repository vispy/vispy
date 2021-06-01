# -*- coding: utf-8 -*-

import numpy as np
from vispy import scene

from vispy.geometry import create_cube, create_sphere
from vispy.testing import (TestingCanvas, requires_application,
                           run_tests_if_main, requires_pyopengl)
from vispy.visuals.filters import WireframeFilter

import pytest


@requires_pyopengl()
def test_mesh_color():
    # Create visual
    vertices, filled_indices, outline_indices = create_cube()
    axis = scene.visuals.Mesh(vertices['position'], outline_indices,
                              color='black', mode='lines')

    # Change color (regression test for a bug that caused this to reset
    # the vertex data to None)

    axis.color = (0.1, 0.3, 0.7, 0.9)

    new_vertices = axis.mesh_data.get_vertices()

    np.testing.assert_allclose(axis.color.rgba, (0.1, 0.3, 0.7, 0.9))
    np.testing.assert_allclose(vertices['position'], new_vertices)


@requires_pyopengl()
@requires_application()
@pytest.mark.parametrize('shading', [None, 'flat', 'smooth'])
def test_mesh_shading_change_from_none(shading):
    # Regression test for #2041: exception raised when changing the shading
    # mode with shading=None initially.
    size = (45, 40)
    with TestingCanvas(size=size) as c:
        v = c.central_widget.add_view(border_width=0)
        vertices = np.array([(0, 0, 0), (0, 0, 1), (1, 0, 0)], dtype=float)
        faces = np.array([(0, 1, 2)])
        mesh = scene.visuals.Mesh(vertices=vertices, faces=faces, shading=None)
        v.add(mesh)
        c.render()
        # This below should not fail.
        mesh.shading = shading
        c.render()


@requires_pyopengl()
@requires_application()
@pytest.mark.parametrize('shading', [None, 'flat', 'smooth'])
def test_mesh_shading_filter(shading):
    size = (45, 40)
    with TestingCanvas(size=size, bgcolor="k") as c:
        v = c.central_widget.add_view(border_width=0)
        # Create visual
        mdata = create_sphere(20, 40, radius=20)
        mesh = scene.visuals.Mesh(meshdata=mdata,
                                  shading=shading,
                                  color=(0.1, 0.3, 0.7, 0.9))
        v.add(mesh)
        from vispy.visuals.transforms import STTransform
        mesh.transform = STTransform(translate=(20, 20))
        mesh.transforms.scene_transform = STTransform(scale=(1, 1, 0.01))

        rendered = c.render()[..., 0]  # R channel only
        if shading in ("flat", "smooth"):
            # there should be a gradient, not solid colors
            assert np.unique(rendered).size >= 28
            # sphere/circle starts "dark" on the left and gets brighter
            # then hits a bright spot and decreases after
            invest_row = rendered[23].astype(np.float64)
            # overall, we should be increasing brightness up to a "bright spot"
            assert (np.diff(invest_row[:29]) >= -1).all()
        else:
            assert np.unique(rendered).size == 2


@requires_pyopengl()
def test_mesh_bounds():
    # Create 3D visual
    vertices, filled_indices, outline_indices = create_cube()
    axis = scene.visuals.Mesh(vertices['position'], outline_indices,
                              color='black', mode='lines')

    # Test bounds for all 3 axes
    for i in range(3):
        np.testing.assert_allclose(axis.bounds(i), (-1.0, 1.0))

    # Create 2D visual using projection of cube
    axis = scene.visuals.Mesh(vertices['position'][:, :2], outline_indices,
                              color='black', mode='lines')

    # Test bounds for first 2 axes
    for i in range(2):
        np.testing.assert_allclose(axis.bounds(i), (-1.0, 1.0))
    # Test bounds for 3rd axis
    np.testing.assert_allclose(axis.bounds(2), (0.0, 0.0))


@requires_pyopengl()
@requires_application()
def test_mesh_wireframe_filter():
    size = (45, 40)
    with TestingCanvas(size=size, bgcolor="k") as c:
        v = c.central_widget.add_view(border_width=0)
        # Create visual
        mdata = create_sphere(20, 40, radius=20)
        mesh = scene.visuals.Mesh(meshdata=mdata,
                                  shading=None,
                                  color=(0.1, 0.3, 0.7, 0.9))
        wireframe_filter = WireframeFilter(color='red')
        mesh.attach(wireframe_filter)
        v.add(mesh)
        from vispy.visuals.transforms import STTransform
        mesh.transform = STTransform(translate=(20, 20))
        mesh.transforms.scene_transform = STTransform(scale=(1, 1, 0.01))

        rendered_with_wf = c.render()
        assert np.unique(rendered_with_wf[..., 0]).size >= 50

        wireframe_filter.enabled = False
        rendered_wo_wf = c.render()
        # the result should be completely different
        # assert not allclose
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_with_wf, rendered_wo_wf)

        wireframe_filter.enabled = True
        wireframe_filter.wireframe_only = True
        rendered_with_wf_only = c.render()
        # the result should be different from the two cases above
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_with_wf_only, rendered_with_wf)
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_with_wf_only, rendered_wo_wf)

        wireframe_filter.enabled = True
        wireframe_filter.wireframe_only = False
        wireframe_filter.faces_only = True
        rendered_with_faces_only = c.render()
        # the result should be different from the cases above
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_with_faces_only, rendered_with_wf)
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_with_faces_only, rendered_wo_wf)
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_with_faces_only, rendered_with_wf_only)


@requires_pyopengl()
@requires_application()
def test_mesh_normals():
    size = (45, 40)
    with TestingCanvas(size=size, bgcolor="k") as c:
        v = c.central_widget.add_view(border_width=0)
        # Create visual
        mdata = create_sphere(20, 40, radius=20)
        mesh = scene.visuals.Mesh(meshdata=mdata,
                                  shading=None,
                                  color=(0.1, 0.1, 0.1, 1.0))
        v.add(mesh)

        from vispy.visuals.transforms import STTransform
        local_transform = STTransform(translate=(20, 20))
        scene_transform = STTransform(scale=(1, 1, 0.01))
        mesh.transform = local_transform
        mesh.transforms.scene_transform = scene_transform

        rendered_without_normals = c.render()
        # The color should be of low intensity.
        assert np.all((rendered_without_normals[..., 0:3]) < 32)

        face_normals = scene.visuals.MeshNormals(mdata, primitive="face",
                                                 color=(1, 0, 0))
        face_normals.parent = mesh
        # XXX: This seems to be repeated. Could this be set on a higher level?
        face_normals.transforms.scene_transform = scene_transform
        rendered_with_face_normals = c.render()
        face_normals.parent = None
        # There should be some pixels with brighter red.
        assert np.sum(rendered_with_face_normals[..., 0] > 128) > 64
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_without_normals, rendered_with_face_normals)

        vertex_normals = scene.visuals.MeshNormals(mdata, primitive="vertex",
                                                   color=(0, 1, 0))
        vertex_normals.parent = mesh
        # XXX: Same as above.
        vertex_normals.transforms.scene_transform = scene_transform
        rendered_with_vertex_normals = c.render()
        vertex_normals.parent = None
        # There should be some pixels with brighter green.
        assert np.sum(rendered_with_vertex_normals[..., 1] > 128) > 64
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_without_normals, rendered_with_vertex_normals)
        pytest.raises(AssertionError, np.testing.assert_allclose,
                      rendered_with_face_normals, rendered_with_vertex_normals)


run_tests_if_main()
