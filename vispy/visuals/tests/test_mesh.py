# -*- coding: utf-8 -*-

import numpy as np
from vispy import scene

from vispy.geometry import create_cube, create_sphere
from vispy.testing import (TestingCanvas, requires_application,
                           run_tests_if_main, requires_pyopengl)

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
def test_mesh_shading_filter(shading):
    size = (45, 40)
    with TestingCanvas(size=size, bgcolor="k") as c:
        v = c.central_widget.add_view(border_width=0)
        # Create visual
        # vertices, filled_indices, outline_indices = create_cube()
        mdata = create_sphere(20, 40, radius=20)
        axis = scene.visuals.Mesh(meshdata=mdata,
                                  shading=shading,
                                  color=(0.1, 0.3, 0.7, 0.9))
        v.add(axis)
        from vispy.visuals.transforms import STTransform
        axis.transform = STTransform(translate=(20, 20))
        axis.transforms.scene_transform = STTransform(scale=(1, 1, 0.01))

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


run_tests_if_main()
