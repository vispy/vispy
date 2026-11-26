# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import numpy as np
from numpy.testing import assert_array_equal, assert_allclose

from vispy.testing import run_tests_if_main
from vispy.geometry import (create_box, create_cube, create_cylinder,
                            create_sphere, create_plane, create_grid_mesh,
                            MeshData)


def test_box():
    """Test box function"""
    vertices, filled, outline = create_box()
    assert_array_equal(np.arange(len(vertices)), np.unique(filled))
    assert_array_equal(np.arange(len(vertices)), np.unique(outline))


def test_cube():
    """Test cube function"""
    vertices, filled, outline = create_cube()
    assert_array_equal(np.arange(len(vertices)), np.unique(filled))
    assert_array_equal(np.arange(len(vertices)), np.unique(outline))


def test_sphere():
    """Test sphere function"""
    md = create_sphere(rows=10, cols=20, radius=10, method='latitude')
    radii = np.sqrt((md.get_vertices() ** 2).sum(axis=1))
    assert radii.dtype.type is np.float32
    assert_allclose(radii, np.ones_like(radii) * 10, atol=1e-06)
    md = create_sphere(subdivisions=5, radius=10, method='ico')
    radii = np.sqrt((md.get_vertices() ** 2).sum(axis=1))
    assert radii.dtype.type is np.float32
    assert_allclose(radii, np.ones_like(radii) * 10, atol=1e-06)
    md = create_sphere(rows=20, cols=20, depth=20, radius=10, method='cube')
    radii = np.sqrt((md.get_vertices() ** 2).sum(axis=1))
    assert radii.dtype.type is np.float32
    assert_allclose(radii, np.ones_like(radii) * 10, atol=1e-06)


def test_cylinder():
    """Test cylinder function"""
    md = create_cylinder(10, 20, radius=[10, 10])
    radii = np.sqrt((md.get_vertices()[:, :2] ** 2).sum(axis=1))
    assert_allclose(radii, np.ones_like(radii) * 10)


def test_plane():
    """Test plane function"""
    vertices, filled, outline = create_plane()
    assert_array_equal(np.arange(len(vertices)), np.unique(filled))
    assert_array_equal(np.arange(len(vertices)), np.unique(outline))


def test_grid_mesh():
    """Test create_grid_mesh produces consistent face and vertex normals."""
    # Regression test for gh-2606: XZ grid in Y=0 plane
    xs, zs = np.meshgrid(np.linspace(-2, 2, 3), np.linspace(-2, 2, 5),
                         indexing='ij')
    ys = np.zeros_like(xs)
    vertices, faces = create_grid_mesh(xs, ys, zs)
    assert len(vertices) == xs.size
    assert len(faces) == 2 * (xs.shape[0] - 1) * (xs.shape[1] - 1)
    assert_array_equal(np.arange(len(vertices)), np.unique(faces))

    mesh = MeshData(vertices=vertices, faces=faces)
    face_normals = mesh.get_face_normals()
    unit_face_normals = (face_normals
                         / np.linalg.norm(face_normals, axis=1, keepdims=True))
    assert_allclose(
        unit_face_normals,
        np.broadcast_to([0., 1., 0.], face_normals.shape))
    assert_allclose(
        mesh.get_vertex_normals(),
        np.broadcast_to([0., 1., 0.], vertices.shape))

    # XY grid in Z=0 plane should orient normals consistently along +z
    xs_xy, ys_xy = np.meshgrid(np.linspace(-1, 1, 4), np.linspace(-1, 1, 3),
                               indexing='xy')
    zs_xy = np.zeros_like(xs_xy)
    verts_xy, faces_xy = create_grid_mesh(xs_xy, ys_xy, zs_xy)
    mesh_xy = MeshData(vertices=verts_xy, faces=faces_xy)
    assert_allclose(
        mesh_xy.get_vertex_normals(),
        np.broadcast_to([0., 0., 1.], verts_xy.shape))

    # Smooth heightfield should have no inverted triangles
    ys_curved = 0.2 * np.sin(xs) * np.cos(zs)
    verts_c, faces_c = create_grid_mesh(xs, ys_curved, zs)
    mesh_c = MeshData(vertices=verts_c, faces=faces_c)
    assert np.all(mesh_c.get_face_normals()[:, 1] > 0)
    assert np.all(mesh_c.get_vertex_normals()[:, 1] > 0)


run_tests_if_main()
