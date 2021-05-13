# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""Miscellaneous functions"""

import numpy as np


###############################################################################
# These fast normal calculation routines are adapted from mne-python

def _fast_cross_3d(x, y):
    """Compute cross product between list of 3D vectors

    Much faster than np.cross() when the number of cross products
    becomes large (>500). This is because np.cross() methods become
    less memory efficient at this stage.

    Parameters
    ----------
    x : array
        Input array 1.
    y : array
        Input array 2.

    Returns
    -------
    z : array
        Cross product of x and y.

    Notes
    -----
    x and y must both be 2D row vectors. One must have length 1, or both
    lengths must match.
    """
    assert x.ndim == 2
    assert y.ndim == 2
    assert x.shape[1] == 3
    assert y.shape[1] == 3
    assert (x.shape[0] == 1 or y.shape[0] == 1) or x.shape[0] == y.shape[0]
    if max([x.shape[0], y.shape[0]]) >= 500:
        return np.c_[x[:, 1] * y[:, 2] - x[:, 2] * y[:, 1],
                     x[:, 2] * y[:, 0] - x[:, 0] * y[:, 2],
                     x[:, 0] * y[:, 1] - x[:, 1] * y[:, 0]]
    else:
        return np.cross(x, y)


def _calculate_normals(rr, tris):
    """Efficiently compute vertex normals for triangulated surface"""
    # ensure highest precision for our summation/vectorization "trick"
    rr = rr.astype(np.float64)
    # first, compute triangle normals
    r1 = rr[tris[:, 0], :]
    r2 = rr[tris[:, 1], :]
    r3 = rr[tris[:, 2], :]
    tri_nn = _fast_cross_3d((r2 - r1), (r3 - r1))

    #   Triangle normals and areas
    size = np.sqrt(np.sum(tri_nn * tri_nn, axis=1))
    size[size == 0] = 1.0  # prevent ugly divide-by-zero
    tri_nn /= size[:, np.newaxis]

    npts = len(rr)

    # the following code replaces this, but is faster (vectorized):
    #
    # for p, verts in enumerate(tris):
    #     nn[verts, :] += tri_nn[p, :]
    #
    nn = np.zeros((npts, 3))
    for verts in tris.T:  # note this only loops 3x (number of verts per tri)
        for idx in range(3):  # x, y, z
            nn[:, idx] += np.bincount(verts.astype(np.int32),
                                      tri_nn[:, idx], minlength=npts)
    size = np.sqrt(np.sum(nn * nn, axis=1))
    size[size == 0] = 1.0  # prevent ugly divide-by-zero
    nn /= size[:, np.newaxis]
    return nn


def resize(image, shape, kind='linear'):
    """Resize an image

    Parameters
    ----------
    image : ndarray
        Array of shape (N, M, ...).
    shape : tuple
        2-element shape.
    kind : str
        Interpolation, either "linear" or "nearest".

    Returns
    -------
    scaled_image : ndarray
        New image, will have dtype np.float64.
    """
    image = np.array(image, float)
    shape = np.array(shape, int)
    if shape.ndim != 1 or shape.size != 2:
        raise ValueError('shape must have two elements')
    if image.ndim < 2:
        raise ValueError('image must have two dimensions')
    if not isinstance(kind, str) or kind not in ('nearest', 'linear'):
        raise ValueError('mode must be "nearest" or "linear"')

    r = np.linspace(0, image.shape[0] - 1, shape[0])
    c = np.linspace(0, image.shape[1] - 1, shape[1])
    if kind == 'linear':
        r_0 = np.floor(r).astype(int)
        c_0 = np.floor(c).astype(int)
        r_1 = r_0 + 1
        c_1 = c_0 + 1

        top = (r_1 - r)[:, np.newaxis]
        bot = (r - r_0)[:, np.newaxis]
        lef = (c - c_0)[np.newaxis, :]
        rig = (c_1 - c)[np.newaxis, :]

        c_1 = np.minimum(c_1, image.shape[1] - 1)
        r_1 = np.minimum(r_1, image.shape[0] - 1)
        for arr in (top, bot, lef, rig):
            arr.shape = arr.shape + (1,) * (image.ndim - 2)
        out = top * rig * image[r_0][:, c_0, ...]
        out += bot * rig * image[r_1][:, c_0, ...]
        out += top * lef * image[r_0][:, c_1, ...]
        out += bot * lef * image[r_1][:, c_1, ...]
    else:  # kind == 'nearest'
        r = np.round(r).astype(int)
        c = np.round(c).astype(int)
        out = image[r][:, c, ...]
    return out
