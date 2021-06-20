#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Very simple transformation library that is needed for some examples.
"""

from __future__ import division

# Note: we use functions (e.g. sin) from math module because they're faster

import math
import numpy as np


def translate(offset, dtype=None):
    """Translate by an offset (x, y, z) .

    Parameters
    ----------
    offset : array-like, shape (3,)
        Translation in x, y, z.
    dtype : dtype | None
        Output type (if None, don't cast).

    Returns
    -------
    M : ndarray
        Transformation matrix describing the translation.
    """
    assert len(offset) == 3
    x, y, z = offset
    M = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [x, y, z, 1.0],
        ],
        dtype,
    )
    return M


def scale(s, dtype=None):
    """Non-uniform scaling along the x, y, and z axes

    Parameters
    ----------
    s : array-like, shape (3,)
        Scaling in x, y, z.
    dtype : dtype | None
        Output type (if None, don't cast).

    Returns
    -------
    M : ndarray
        Transformation matrix describing the scaling.
    """
    assert len(s) == 3
    return np.array(np.diag(np.concatenate([s, (1.0,)])), dtype)


def rotate(angle, axis, dtype=None):
    """The 3x3 rotation matrix for rotation about a vector.

    Parameters
    ----------
    angle : float
        The angle of rotation, in degrees.
    axis : ndarray
        The x, y, z coordinates of the axis direction vector.

    Returns
    -------
    M : ndarray
        Transformation matrix describing the rotation.
    """
    angle = np.radians(angle)
    assert len(axis) == 3
    x, y, z = axis / np.linalg.norm(axis)
    c, s = math.cos(angle), math.sin(angle)
    cx, cy, cz = (1 - c) * x, (1 - c) * y, (1 - c) * z
    M = np.array(
        [
            [cx * x + c, cy * x - z * s, cz * x + y * s, 0.0],
            [cx * y + z * s, cy * y + c, cz * y - x * s, 0.0],
            [cx * z - y * s, cy * z + x * s, cz * z + c, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype,
    ).T
    return M


def ortho(left, right, bottom, top, znear, zfar):
    """Create orthographic projection matrix

    Parameters
    ----------
    left : float
        Left coordinate of the field of view.
    right : float
        Right coordinate of the field of view.
    bottom : float
        Bottom coordinate of the field of view.
    top : float
        Top coordinate of the field of view.
    znear : float
        Near coordinate of the field of view.
    zfar : float
        Far coordinate of the field of view.

    Returns
    -------
    M : ndarray
        Orthographic projection matrix (4x4).
    """
    assert right != left
    assert bottom != top
    assert znear != zfar

    M = np.zeros((4, 4), dtype=np.float32)
    M[0, 0] = +2.0 / (right - left)
    M[3, 0] = -(right + left) / float(right - left)
    M[1, 1] = +2.0 / (top - bottom)
    M[3, 1] = -(top + bottom) / float(top - bottom)
    M[2, 2] = -2.0 / (zfar - znear)
    M[3, 2] = -(zfar + znear) / float(zfar - znear)
    M[3, 3] = 1.0
    return M


def frustum(left, right, bottom, top, znear, zfar):
    """Create view frustum

    Parameters
    ----------
    left : float
        Left coordinate of the field of view.
    right : float
        Right coordinate of the field of view.
    bottom : float
        Bottom coordinate of the field of view.
    top : float
        Top coordinate of the field of view.
    znear : float
        Near coordinate of the field of view.
    zfar : float
        Far coordinate of the field of view.

    Returns
    -------
    M : ndarray
        View frustum matrix (4x4).
    """
    assert right != left
    assert bottom != top
    assert znear != zfar

    M = np.zeros((4, 4), dtype=np.float32)
    M[0, 0] = +2.0 * znear / float(right - left)
    M[2, 0] = (right + left) / float(right - left)
    M[1, 1] = +2.0 * znear / float(top - bottom)
    M[2, 1] = (top + bottom) / float(top - bottom)
    M[2, 2] = -(zfar + znear) / float(zfar - znear)
    M[3, 2] = -2.0 * znear * zfar / float(zfar - znear)
    M[2, 3] = -1.0
    return M


def perspective(fovy, aspect, znear, zfar):
    """Create perspective projection matrix

    Parameters
    ----------
    fovy : float
        The field of view along the y axis.
    aspect : float
        Aspect ratio of the view.
    znear : float
        Near coordinate of the field of view.
    zfar : float
        Far coordinate of the field of view.

    Returns
    -------
    M : ndarray
        Perspective projection matrix (4x4).
    """
    assert znear != zfar
    h = math.tan(fovy / 360.0 * math.pi) * znear
    w = h * aspect
    return frustum(-w, w, -h, h, znear, zfar)


def affine_map(points1, points2):
    """Find a 3D transformation matrix that maps points1 onto points2.

    Arguments are specified as arrays of four 3D coordinates, shape (4, 3).
    """
    A = np.ones((4, 4))
    A[:, :3] = points1
    B = np.ones((4, 4))
    B[:, :3] = points2

    # solve 3 sets of linear equations to determine
    # transformation matrix elements
    matrix = np.eye(4)
    for i in range(3):
        # solve Ax = B; x is one row of the desired transformation matrix
        matrix[i] = np.linalg.solve(A, B[:, i])

    return matrix


def non_singular(vmin, vmax, expander=0.001, tiny=1e-15, increasing=True):
    """Modify the endpoints of a range as needed to avoid singularities.

    Parameters
    ----------
    vmin, vmax : float
        The initial endpoints.
    expander : float, default: 0.001
        Fractional amount by which *vmin* and *vmax* are expanded if
        the original interval is too small, based on *tiny*.
    tiny : float, default: 1e-15
        Threshold for the ratio of the interval to the maximum absolute
        value of its endpoints.  If the interval is smaller than
        this, it will be expanded.  This value should be around
        1e-15 or larger; otherwise the interval will be approaching
        the double precision resolution limit.
    increasing : bool, default: True
        If True, swap *vmin*, *vmax* if *vmin* > *vmax*.

    Returns
    -------
    vmin, vmax : float
        Endpoints, expanded and/or swapped if necessary.
        If either input is inf or NaN, or if both inputs are 0 or very
        close to zero, it returns -*expander*, *expander*.
    """

    if (not np.isfinite(vmin)) or (not np.isfinite(vmax)):
        return -expander, expander

    swapped = False
    if vmax < vmin:
        vmin, vmax = vmax, vmin
        swapped = True

    # Expand vmin, vmax to float: if they were integer types, they can wrap
    # around in abs (abs(np.int8(-128)) == -128) and vmax - vmin can overflow.
    vmin, vmax = map(float, [vmin, vmax])

    maxabsvalue = max(abs(vmin), abs(vmax))
    if maxabsvalue < (1e6 / tiny) * np.finfo(float).tiny:
        vmin = -expander
        vmax = expander

    elif vmax - vmin <= maxabsvalue * tiny:
        if vmax == 0 and vmin == 0:
            vmin = -expander
            vmax = expander
        else:
            vmin -= expander * abs(vmin)
            vmax += expander * abs(vmax)

    if swapped and not increasing:
        vmin, vmax = vmax, vmin
    return vmin, vmax
