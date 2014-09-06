# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""Miscellaneous functions

    _bbox, _mean_center, _sbox, _distance_from_point
        are adpated from pyformex package
"""

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
            nn[:, idx] += np.bincount(verts, tri_nn[:, idx], minlength=npts)
    size = np.sqrt(np.sum(nn * nn, axis=1))
    size[size == 0] = 1.0  # prevent ugly divide-by-zero
    nn /= size[:, np.newaxis]
    return nn


def _bbox(vertices):
    """Returns the bounding box of a set of vertices.

    The bounding box is the smallest rectangular volume in the global
    coordinates, such that no vertices are outside that volume.

    Parameters
    ----------
    vertices : ndarray, shape (Nv, 3)
        Vertex coordinates.

    Returns
    -------
    bbox : ndarray, shape (2, 3)
        the first point contains the minimal coordinates,
        the second has the maximal ones.

    Example
    -------

      >>> vertices = np.array([[0.,0.,0.],[3.,0.,0.],[0.,3.,0.]])
      >>> print(_bbox(vertices))
      [[ 0.  0.  0.]
       [ 3.  3.  0.]]
    """
    bbox = None
    if np.asarray(vertices) is vertices:
        if vertices.shape[1] <= 3:
            bbox = np.row_stack([vertices.min(axis=0), vertices.max(axis=0)])

    return bbox


def _mean_center(vertices):
    """Returns the centroid of a set of vertices.

    The mean_center of a set of vertices is the point whose coordinates
    are the mean values of all points.

    Parameters
    ----------
    vertices : ndarray, shape (Nv, 3)
        Vertex coordinates.

    Returns
    -------
    center : ndarray, shape (3,)
        the coordinates of the center

    Example
    -------

      >>> vertices = np.array([[0.,0.,0.],[3.,0.,0.],[0.,3.,0.]])
      >>> print(_mean_center(vertices))
      [ 1.  1.  0.]
    """
    center = None
    if np.asarray(vertices) is vertices:
        if vertices.shape[1] <= 3:
            center = vertices.mean(axis=0)
    return center


def _distance_from_point(point, vertices):
    """Returns the distance of all vertices from the point.

    Parameters
    ----------
    point : ndarray, shape (3,)
        Vertice coordinate.
    vertices : ndarray, shape (Nv, 3)
        Vertex coordinates.
    Returns
    -------
    cdist : ndarray, shape (Nv,)
        the distance of each vertices to point. All distance values
        are positive or zero.

    Example
    -------

      >>> vertices = np.array([[0.,0.,0.],[3.,0.,0.],[0.,3.,0.]])
      >>> point = np.array([0.,0.,0.])
      >>> print(_distance_from_point(point, vertices))
      [ 0.  3.  3.]
    """
    cdist = None
    if np.asarray(vertices) is vertices and np.asarray(point) is point:
        if vertices.shape[1] <= 3 and point.ndim == 1 and point.size == 3:
            cdist = vertices-point
            cdist = np.sqrt(np.sum(cdist*cdist, -1))
    return cdist


def _bsphere(vertices):
    """Returns the radius and the center of a bounding sphere  of a set
       of vertex this bounding sphere is near of the smallest closet sphere.
       the center is bbox center
    Parameters
    ----------
    vertices : ndarray, shape (Nv, 3)
        Vertex coordinates.

    Returns
    -------
    center : ndarray, shape (3,)
    radius : float

    Example
    -------

      >>> vertices = Coords([[[0.,0.,0.],[3.,0.,0.],[0.,3.,0.]]])
      print(_bsphere(vertices))
      [ 1.5,  1.5,  0. ], 2.1213203435596424
    """
    radius = 0
    center = None
    if np.asarray(vertices) is vertices:
        if vertices.shape[1] <= 3:
            center = _mean_center(_bbox(vertices))
            radius = _distance_from_point(center, vertices).max()
    return center, radius


def _besphere(vertices, tol=1e-3, kmax=100):
    """Returns the radius and the center of the smallest bounding sphere  of a set
       of vertex this bounding sphere is near (tol factor) of the smallest
       closet sphere. this function is based on the paper <<Two algorithms for
             the minimum enclosing ball problem, E. Alper Yildirim, 2007 >>

    Parameters
    ----------
    vertices : ndarray, shape (Nv, 3)
        Vertex coordinates.
    tol: float
        read the publication
    niter_max: int
        read the publication

    Returns
    -------
    ck : ndarray, shape (3,)
    radius : float

    Example
    -------

      >>> vertices = Coords([[[0.,0.,0.],[3.,0.,0.],[0.,3.,0.]]])
      print(_besphere(vertices))
      [ 1.5,  1.5,  0. ], 2.1213203435596424
    """
    # Initialisation of algorithm
    alpha = np.argmax(_distance_from_point(vertices[0, :], vertices))
    point = vertices[alpha, :]
    beta = np.argmax(_distance_from_point(point, vertices))
    point1 = vertices[beta, :]
    ck = 0.5*point+0.5*point1
    gammak = 0.25*np.linalg.norm(point-point1)**2
    kk = np.argmax(_distance_from_point(ck, vertices))
    point = vertices[kk, :]
    dist = np.linalg.norm(point-ck)
    deltak = 0.0
    if (gammak != 0.0):
        deltak = dist**2/gammak-1.0

    for k in range(kmax):
        if (np.abs(deltak) < ((1.0+tol)**2-1.0)):
            break
        lambdak = deltak/(2.0*(1.0+deltak))
        ck = (1.0-lambdak)*ck+lambdak*point
        gammak = gammak*(1.0+deltak**2/(1.0+deltak))
        kk = np.argmax(_distance_from_point(ck, vertices))
        point = vertices[kk, :]
        dist = np.linalg.norm(point-ck)
        deltak = dist**2/gammak-1.0

    radius = np.sqrt((1.0+deltak)*gammak)

    return ck, radius
