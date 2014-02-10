#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Very simple transformation library that is needed for some examples.
"""

# Note: we use functions (e.g. sin) from math module because they're faster

import math
import numpy as np


def translate(M, x, y=None, z=None):
    """Translate by an offset (x, y, z) .

    Parameters
    ----------
    M : array
        Original transformation (4x4).
    x : float
        X coordinate of a translation vector.
    y : float | None
        Y coordinate of translation vector. If None, `x` will be used.
    z : float | None
        Z coordinate of translation vector. If None, `x` will be used.

    Returns
    -------
    M : array
        Updated transformation (4x4). Note that this function operates
        in-place.
    """
    y = x if y is None else y
    z = x if z is None else z
    T = np.array([[1.0, 0.0, 0.0, x],
                  [0.0, 1.0, 0.0, y],
                  [0.0, 0.0, 1.0, z],
                  [0.0, 0.0, 0.0, 1.0]], dtype=M.dtype).T
    M[...] = np.dot(M, T)
    return M


def scale(M, x, y=None, z=None):
    """Non-uniform scaling along the x, y, and z axes

    Parameters
    ----------
    M : array
        Original transformation (4x4).
    x : float
        X coordinate of the translation vector.
    y : float | None
        Y coordinate of the translation vector. If None, `x` will be used.
    z : float | None
        Z coordinate of the translation vector. If None, `x` will be used.

    Returns
    -------
    M : array
        Updated transformation (4x4). Note that this function operates
        in-place.
    """
    y = x if y is None else y
    z = x if z is None else z
    S = np.array([[x, 0.0, 0.0, 0.0],
                  [0.0, y, 0.0, 0.0],
                  [0.0, 0.0, z, 0.0],
                  [0.0, 0.0, 0.0, 1.0]], dtype=M.dtype).T
    M[...] = np.dot(M, S)
    return M


def xrotate(M, theta):
    """Rotate about the X axis

    Parameters
    ----------
    M : array
        Original transformation (4x4).
    theta : float
        Specifies the angle of rotation, in degrees.

    Returns
    -------
    M : array
        Updated transformation (4x4). Note that this function operates
        in-place.
    """
    t = math.pi * theta / 180.
    cosT = math.cos(t)
    sinT = math.sin(t)
    R = np.array([[1.0, 0.0, 0.0, 0.0],
                  [0.0, cosT, -sinT, 0.0],
                  [0.0, sinT, cosT, 0.0],
                  [0.0, 0.0, 0.0, 1.0]], dtype=M.dtype)
    M[...] = np.dot(M, R)
    return M


def yrotate(M, theta):
    """Rotate about the Y axis

    Parameters
    ----------
    M : array
        Original transformation (4x4).
    theta : float
        Specifies the angle of rotation, in degrees.

    Returns
    -------
    M : array
        Updated transformation (4x4). Note that this function operates
        in-place.
    """
    t = math.pi * theta / 180
    cosT = math.cos(t)
    sinT = math.sin(t)
    R = np.array(
        [[cosT, 0.0, sinT, 0.0],
         [0.0, 1.0, 0.0, 0.0],
         [-sinT, 0.0, cosT, 0.0],
         [0.0, 0.0, 0.0, 1.0]], dtype=M.dtype)
    M[...] = np.dot(M, R)
    return M


def zrotate(M, theta):
    """Rotate about the Z axis

    Parameters
    ----------
    M : array
        Original transformation (4x4).
    theta : float
        Specifies the angle of rotation, in degrees.

    Returns
    -------
    M : array
        Updated transformation (4x4). Note that this function operates
        in-place.
    """
    t = math.pi * theta / 180
    cosT = math.cos(t)
    sinT = math.sin(t)
    R = np.array(
        [[cosT, -sinT, 0.0, 0.0],
         [sinT, cosT, 0.0, 0.0],
         [0.0, 0.0, 1.0, 0.0],
         [0.0, 0.0, 0.0, 1.0]], dtype=M.dtype)
    M[...] = np.dot(M, R)
    return M


def rotate(M, angle, x, y, z, point=None):
    """Rotation about a vector

    Parameters
    ----------
    M : array
        Original transformation (4x4).
    angle : float
        Specifies the angle of rotation, in degrees.
    x : float
        X coordinate of the angle of rotation vector.
    y : float | None
        Y coordinate of the angle of rotation vector.
    z : float | None
        Z coordinate of the angle of rotation vector.

    Returns
    -------
    M : array
        Updated transformation (4x4). Note that this function operates
        in-place.
    """
    angle = math.pi * angle / 180
    c, s = math.cos(angle), math.sin(angle)
    n = math.sqrt(x * x + y * y + z * z)
    x /= n
    y /= n
    z /= n
    cx, cy, cz = (1 - c) * x, (1 - c) * y, (1 - c) * z
    R = np.array([[cx * x + c, cy * x - z * s, cz * x + y * s, 0],
                  [cx * y + z * s, cy * y + c, cz * y - x * s, 0],
                  [cx * z - y * s, cy * z + x * s, cz * z + c, 0],
                  [0, 0, 0, 1]], dtype=M.dtype).T
    M[...] = np.dot(M, R)
    return M


def ortho(left, right, bottom, top, znear, zfar):
    """Create orthographic projection matrix

    Parameters
    ----------
    left : float
        Left coordinate of the field of view.
    right : float
        Left coordinate of the field of view.
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
    M : array
        Orthographic projection matrix (4x4).
    """
    assert(right != left)
    assert(bottom != top)
    assert(znear != zfar)

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
        Left coordinate of the field of view.
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
    M : array
        View frustum matrix (4x4).
    """
    assert(right != left)
    assert(bottom != top)
    assert(znear != zfar)

    M = np.zeros((4, 4), dtype=np.float32)
    M[0, 0] = +2.0 * znear / (right - left)
    M[2, 0] = (right + left) / (right - left)
    M[1, 1] = +2.0 * znear / (top - bottom)
    M[3, 1] = (top + bottom) / (top - bottom)
    M[2, 2] = -(zfar + znear) / (zfar - znear)
    M[3, 2] = -2.0 * znear * zfar / (zfar - znear)
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
    M : array
        Perspective projection matrix (4x4).
    """
    assert(znear != zfar)
    h = math.tan(fovy / 360.0 * math.pi) * znear
    w = h * aspect
    return frustum(-w, w, -h, h, znear, zfar)
