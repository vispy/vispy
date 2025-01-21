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


def test_vertex_normals_indexed_none():
    dtype_float = np.float32
    dtype_int = np.int64
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]],
                        dtype=dtype_float)
    faces = np.array([[0, 2, 1], [0, 3, 2], [0, 1, 3]], dtype=dtype_int)
    mesh = MeshData(vertices=vertices, faces=faces)
    vertex_normals_unnormalized = np.array(
        [[-1, -1, -1], [0, -1, -1], [-1, 0, -1], [-1, -1, 0]],
        dtype=dtype_float)
    norms = np.sqrt((vertex_normals_unnormalized**2).sum(axis=1,
                                                         keepdims=True))
    expected_vertex_normals = vertex_normals_unnormalized / norms

    computed_vertex_normals = mesh.get_vertex_normals(indexed=None)

    assert_array_equal(expected_vertex_normals, computed_vertex_normals)


def test_vertex_normals_indexed_faces():
    dtype_float = np.float32
    dtype_int = np.int64
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]],
                        dtype=dtype_float)
    faces = np.array([[0, 2, 1], [0, 3, 2], [0, 1, 3]], dtype=dtype_int)
    mesh = MeshData(vertices=vertices, faces=faces)
    vertex_normals_unnormalized = np.array(
        [[-1, -1, -1], [0, -1, -1], [-1, 0, -1], [-1, -1, 0]],
        dtype=dtype_float)
    norms = np.sqrt((vertex_normals_unnormalized**2).sum(axis=1,
                                                         keepdims=True))
    vertex_normals = vertex_normals_unnormalized / norms
    expected_vertex_normals = vertex_normals[faces]

    computed_vertex_normals = mesh.get_vertex_normals(indexed="faces")

    assert_array_equal(expected_vertex_normals, computed_vertex_normals)


def test_face_normals_indexed_none():
    dtype_float = np.float32
    dtype_int = np.int64
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]],
                        dtype=dtype_float)
    faces = np.array([[0, 2, 1], [0, 3, 2], [0, 1, 3]], dtype=dtype_int)
    mesh = MeshData(vertices=vertices, faces=faces)
    expected_face_normals = np.array([[0, 0, -1], [-1, 0, 0], [0, -1, 0]],
                                     dtype=dtype_float)

    computed_face_normals = mesh.get_face_normals(indexed=None)

    assert_array_equal(expected_face_normals, computed_face_normals)


def test_face_normals_indexed_faces():
    dtype_float = np.float32
    dtype_int = np.int64
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]],
                        dtype=dtype_float)
    faces = np.array([[0, 2, 1], [0, 3, 2], [0, 1, 3]], dtype=dtype_int)
    mesh = MeshData(vertices=vertices, faces=faces)
    expected_face_normals = np.array([
        [[0, 0, -1], [0, 0, -1], [0, 0, -1]],
        [[-1, 0, 0], [-1, 0, 0], [-1, 0, 0]],
        [[0, -1, 0], [0, -1, 0], [0, -1, 0]]],
        dtype=dtype_float)

    computed_face_normals = mesh.get_face_normals(indexed="faces")

    assert_array_equal(expected_face_normals, computed_face_normals)


run_tests_if_main()
