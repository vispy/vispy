# -*- coding: utf-8 -*-

import numpy as np
from vispy import scene

from vispy.geometry import create_cube
from vispy.testing import run_tests_if_main, requires_pyopengl


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


run_tests_if_main()
