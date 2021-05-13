# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from numpy.testing import assert_array_equal

from vispy.testing import run_tests_if_main
from vispy.geometry.meshdata import MeshData


def test_meshdata():
    """Test meshdata Class
    It's a unit square cut in two triangular element
    """
    square_vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
                               dtype=np.float64)
    square_faces = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint8)
    square_normals = np.array([[0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]],
                              dtype=np.float64)
    square_edges = np.array([[0, 1], [0, 2], [0, 3], [1, 2], [2, 3]],
                            dtype=np.uint8)

    mesh = MeshData(vertices=square_vertices, faces=square_faces)
    # test vertices and faces assignement
    assert_array_equal(square_vertices, mesh.get_vertices())
    assert_array_equal(square_faces, mesh.get_faces())
    # test normals calculus
    assert_array_equal(square_normals, mesh.get_vertex_normals())
    # test edge calculus
    assert_array_equal(square_edges, mesh.get_edges())


run_tests_if_main()
