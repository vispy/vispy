# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from numpy.testing import assert_array_equal

from vispy.testing import run_tests_if_main
from vispy.geometry.meshdata import MeshData


def test_meshdata():
    dtype_float = np.float64
    dtype_int = np.uint8
    # Three ajacent triangles forming the tip of a tetrahedron at the origin.
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]],
                        dtype=dtype_float)
    faces = np.array([[0, 1, 2], [0, 2, 3], [0, 3, 1]], dtype=dtype_int)
    face_normals = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]],
                            dtype=dtype_float)
    isqrt3 = 1 / np.sqrt(3)
    isqrt2 = 1 / np.sqrt(2)
    vertex_normals = np.array([
        [isqrt3, isqrt3, isqrt3],
        [0, isqrt2, isqrt2],
        [isqrt2, 0, isqrt2],
        [isqrt2, isqrt2, 0]
    ], dtype=dtype_float)
    edges = np.array([[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]],
                     dtype=dtype_int)

    mesh = MeshData(vertices=vertices, faces=faces)
    assert_array_equal(vertices, mesh.get_vertices())
    assert_array_equal(faces, mesh.get_faces())
    assert_array_equal(vertex_normals, mesh.get_vertex_normals())
    assert_array_equal(face_normals, mesh.get_face_normals())
    assert_array_equal(edges, mesh.get_edges())


run_tests_if_main()
