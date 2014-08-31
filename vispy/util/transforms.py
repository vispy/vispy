#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Very simple transformation library that is needed for some examples.

Note that functions that take a matrix as input generally operate on that
matrix in place.
"""

from __future__ import division

# Note: we use functions (e.g. sin) from math module because they're faster

import math
import numpy as np
from numpy.linalg import norm


def translate(offset, dtype = None):
    """Translate by an offset (x, y, z) .

    Parameters
    ----------
    offset : 3-item iterable (e.g. tuple, np array, list) describing
        translation in x, y, z

 
    Returns
    -------
    M : matrix
        transformation matrix describing the translation
    """
    x, y, z = offset
    M = np.matrix([[1.0, 0.0, 0.0, x],
                  [0.0, 1.0, 0.0, y],
                  [0.0, 0.0, 1.0, z],
                  [0.0, 0.0, 0.0, 1.0]], dtype).T
    return M


def scale(s, dtype = None):
    """Non-uniform scaling along the x, y, and z axes

    Parameters
    ----------
    s : 3-item iterable (e.g. tuple, np array, list) describing
        scaling in x, y, z

 
    Returns
    -------
    M : matrix
        transformation matrix describing the scaling
    """
    x, y, z = s
    return np.matrix(np.diag((x,y,z,1.0)), dtype)
   


def rotate(radians, axis, dtype = None):
    """
    Returns a homogeneous transformation matrix that represents a rotation
    around axis by angle (in radians) using Rodrigues' formula
    http://en.wikipedia.org/wiki/Rodrigues%27_rotation_formula

    Parameters
    ----------

    radians: angle, in radians, to rotate around the axis
    
    axis: list, tuple or np array (1D) representing the axis to rotate about
        (does not need to be unit length)
    """

    z=np.matrix(axis, dtype = np.double).T
    #Normalize z
    z=z/math.sqrt(z.T*z)
    ztilde=np.matrix([[0,-z[2],z[1]],[z[2],0,-z[0]],[-z[1],z[0],0]])
    
    # Compute 3x3 rotation matrix
    R=np.eye(3) + math.sin(radians)*ztilde + ((1-math.cos(radians))* ((z*z.T)-np.eye(3)))
    M = np.eye(4)
    M[:3,:3] = R
    
    return np.matrix(M, dtype)

# Actually, param 'degrees' should be called 'angle' since that is the 
# quantity but it is called degrees since that makes it explicit that it is
# in degrees
def rotated(degrees, axis, dtype = None):
    """
    Convenience wrapper for @see rotate that accepts angle in degrees
    """
    return rotate(np.radians(degrees), axis, dtype)
    
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
    M : array
        View frustum matrix (4x4).
    """
    assert(right != left)
    assert(bottom != top)
    assert(znear != zfar)

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
    M : array
        Perspective projection matrix (4x4).
    """
    assert(znear != zfar)
    h = math.tan(fovy / 360.0 * math.pi) * znear
    w = h * aspect
    return frustum(-w, w, -h, h, znear, zfar)


def affine_map(points1, points2):
    """ Find a 3D transformation matrix that maps points1 onto points2.

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
