import numpy as np
from os import path as op
from nose.tools import assert_equal, assert_raises
from numpy.testing import assert_allclose, assert_array_equal

from vispy.util.dataio import (write_mesh, read_mesh, _check_img_lib, crate,
                               imsave, imread)
from vispy.util.misc import _fast_cross_3d
from vispy.util import _TempDir

temp_dir = _TempDir()

has_img_lib = not all(c is None for c in _check_img_lib())
requires_img_lib = np.testing.dec.skipif(not has_img_lib, 'imageio or PIL '
                                         'required')


def test_wavefront():
    """Test wavefront reader"""
    fname_mesh = 'triceratops.obj'

    fname_out = op.join(temp_dir, 'temp.obj')
    mesh1 = read_mesh(fname_mesh)
    assert_raises(ValueError, read_mesh, 'foo')
    assert_raises(ValueError, read_mesh, op.abspath(__file__))
    assert_raises(ValueError, write_mesh, fname_out, mesh1[0], mesh1[1],
                  mesh1[2], mesh1[3], format='foo')
    write_mesh(fname_out, mesh1[0], mesh1[1], mesh1[2], mesh1[3])
    assert_raises(IOError, write_mesh, fname_out, mesh1[0], mesh1[1],
                  mesh1[2], mesh1[3])
    write_mesh(fname_out, mesh1[0], mesh1[1], mesh1[2], mesh1[3],
               overwrite=True)
    mesh2 = read_mesh(fname_out)
    assert_equal(len(mesh1), len(mesh2))
    for m1, m2 in zip(mesh1, mesh2):
        if m1 is None:
            assert_equal(m2, None)
        else:
            assert_allclose(m1, m2)
    # test our efficient normal calculation routine
    assert_allclose(mesh1[2], _slow_calculate_normals(mesh1[0], mesh1[1]),
                    rtol=1e-10, atol=1e-10)


@requires_img_lib
def test_read_write_image():
    """Test reading and writing of images"""
    fname = op.join(temp_dir, 'out.png')
    im1 = crate()
    imsave(fname, im1, format='png')
    im2 = imread(fname)
    assert_allclose(im1, im2)


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
