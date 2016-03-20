# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
import numpy as np
from os import path as op
from numpy.testing import assert_allclose, assert_array_equal

from vispy.io import write_mesh, read_mesh, load_data_file
from vispy.geometry import _fast_cross_3d
from vispy.util import _TempDir
from vispy.testing import run_tests_if_main, assert_equal, assert_raises

temp_dir = _TempDir()


def test_wavefront():
    """Test wavefront reader"""
    fname_mesh = load_data_file('orig/triceratops.obj.gz')
    fname_out = op.join(temp_dir, 'temp.obj')
    mesh1 = read_mesh(fname_mesh)
    assert_raises(IOError, read_mesh, 'foo.obj')
    assert_raises(ValueError, read_mesh, op.abspath(__file__))
    assert_raises(ValueError, write_mesh, fname_out, *mesh1, format='foo')
    write_mesh(fname_out, mesh1[0], mesh1[1], mesh1[2], mesh1[3])
    assert_raises(IOError, write_mesh, fname_out, *mesh1)
    write_mesh(fname_out, *mesh1, overwrite=True)
    mesh2 = read_mesh(fname_out)
    assert_equal(len(mesh1), len(mesh2))
    for m1, m2 in zip(mesh1, mesh2):
        if m1 is None:
            assert_equal(m2, None)
        else:
            assert_allclose(m1, m2, rtol=1e-5)
    # test our efficient normal calculation routine
    assert_allclose(mesh1[2], _slow_calculate_normals(mesh1[0], mesh1[1]),
                    rtol=1e-7, atol=1e-7)


def test_wavefront_non_triangular():
    '''Test wavefront writing with non-triangular faces'''
    vertices = np.array([[0.5, 1.375, 0.],
                         [0.5, 0.625, 0.],
                         [3.25, 1., 0.],
                         [1., 0.375, 0.],
                         [2., 0.375, 0.],
                         [1.5, 0.625, 0.],
                         [1.5, 1.375, 0.],
                         [1., 1.625, 0.],
                         [2., 1.625, 0.]])

    faces = np.array([[1, 0, 7, 6, 5, 3],
                      [4, 5, 6, 8, 2]])
    fname_out = op.join(temp_dir, 'temp.obj')
    write_mesh(fname_out, vertices=vertices,
               faces=faces, normals=None,
               texcoords=None, overwrite=True,
               reshape_faces=False)
    assert_raises(RuntimeError, read_mesh, fname_out)
    with open(fname_out, 'r+') as out_file:
        lines = out_file.readlines()
    assert lines[-1].startswith('f 5 6 7 9 3')
    assert lines[-2].startswith('f 2 1 8 7 6 4')


def _slow_calculate_normals(rr, tris):
    """Efficiently compute vertex normals for triangulated surface"""
    # first, compute triangle normals
    rr = rr.astype(np.float64)
    r1 = rr[tris[:, 0], :]
    r2 = rr[tris[:, 1], :]
    r3 = rr[tris[:, 2], :]
    tri_nn = np.cross((r2 - r1), (r3 - r1))

    #   Triangle normals and areas
    size = np.sqrt(np.sum(tri_nn * tri_nn, axis=1))
    zidx = np.where(size == 0)[0]
    size[zidx] = 1.0  # prevent ugly divide-by-zero
    tri_nn /= size[:, np.newaxis]

    # accumulate the normals
    nn = np.zeros((len(rr), 3))
    for p, verts in enumerate(tris):
        nn[verts] += tri_nn[p, :]
    size = np.sqrt(np.sum(nn * nn, axis=1))
    size[size == 0] = 1.0  # prevent ugly divide-by-zero
    nn /= size[:, np.newaxis]
    return nn


def test_huge_cross():
    """Test cross product with lots of elements
    """
    x = np.random.rand(100000, 3)
    y = np.random.rand(1, 3)
    z = np.cross(x, y)
    zz = _fast_cross_3d(x, y)
    assert_array_equal(z, zz)


run_tests_if_main()
