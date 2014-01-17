#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Very simple transformation library that is needed for some examples.
"""

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
        in-place to modify M.
    """
    y = x if y is None else y
    z = x if z is None else z
    move = np.array([x, y, z], dtype=M.dtype)
    M[:3, 3] += move
    return M


def scale(M, x, y=None, z=None):
    """Non-uniform scaling along the x, y, and z axes

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
        in-place to modify M.
    """
    y = x if y is None else y
    z = x if z is None else z
    M *= np.array([x, y, z, 1], dtype=M.dtype)[np.newaxis, :]
    return M


def xrotate(M,theta):
    t = np.pi * theta / 180.
    cosT = np.cos(t)
    sinT = np.sin(t)
    R = np.array([[ 1.0,  0.0,  0.0, 0.0 ],
                  [ 0.0, cosT,-sinT, 0.0 ],
                  [ 0.0, sinT, cosT, 0.0 ],
                  [ 0.0,  0.0,  0.0, 1.0 ]], dtype=M.dtype)
    M[...] = np.dot(M, R)
    return M


def yrotate(M,theta):
    t = np.pi*theta/180
    cosT = np.cos( t )
    sinT = np.sin( t )
    R = np.array(
        [[ cosT,  0.0, sinT, 0.0 ],
         [ 0.0,   1.0,  0.0, 0.0 ],
         [-sinT,  0.0, cosT, 0.0 ],
         [ 0.0,  0.0,  0.0, 1.0 ]], dtype=M.dtype)
    M[...] = np.dot(M,R)


def zrotate(M,theta):
    t = np.pi*theta/180
    cosT = np.cos( t )
    sinT = np.sin( t )
    R = np.array(
        [[ cosT,-sinT, 0.0, 0.0 ],
         [ sinT, cosT, 0.0, 0.0 ],
         [ 0.0,  0.0,  1.0, 0.0 ],
         [ 0.0,  0.0,  0.0, 1.0 ]], dtype=M.dtype)
    M[...] = np.dot(M,R)


def rotate(M, angle, x, y, z, point=None):
    """
    rotate produces a rotation of angle degrees around the vector (x, y, z).

    Parameters
    ----------
    M
       Current transformation as a numpy array

    angle
       Specifies the angle of rotation, in degrees.

    x, y, z
        Specify the x, y, and z coordinates of a vector, respectively.
    """
    angle = np.pi*angle/180
    c,s = np.cos(angle), np.sin(angle)
    n = np.sqrt(x*x+y*y+z*z)
    x /= n
    y /= n
    z /= n
    cx,cy,cz = (1-c)*x, (1-c)*y, (1-c)*z
    R = np.array([[ cx*x + c  , cy*x - z*s, cz*x + y*s, 0],
                     [ cx*y + z*s, cy*y + c  , cz*y - x*s, 0],
                     [ cx*z - y*s, cy*z + x*s, cz*z + c,   0],
                     [          0,          0,        0,   1]], dtype=M.dtype).T
    M[...] = np.dot(M,R)


def ortho( left, right, bottom, top, znear, zfar ):
    assert( right  != left )
    assert( bottom != top  )
    assert( znear  != zfar )

    M = np.zeros((4,4), dtype=np.float32)
    M[0,0] = +2.0/(right-left)
    M[3,0] = -(right+left)/float(right-left)
    M[1,1] = +2.0/(top-bottom)
    M[3,1] = -(top+bottom)/float(top-bottom)
    M[2,2] = -2.0/(zfar-znear)
    M[3,2] = -(zfar+znear)/float(zfar-znear)
    M[3,3] = 1.0
    return M

def frustum( left, right, bottom, top, znear, zfar ):
    assert( right  != left )
    assert( bottom != top  )
    assert( znear  != zfar )

    M = np.zeros((4,4), dtype=np.float32)
    M[0,0] = +2.0*znear/(right-left)
    M[2,0] = (right+left)/(right-left)
    M[1,1] = +2.0*znear/(top-bottom)
    M[3,1] = (top+bottom)/(top-bottom)
    M[2,2] = -(zfar+znear)/(zfar-znear)
    M[3,2] = -2.0*znear*zfar/(zfar-znear)
    M[2,3] = -1.0
    return M

def perspective(fovy, aspect, znear, zfar):
    assert( znear != zfar )
    h = np.tan(fovy / 360.0 * np.pi) * znear
    w = h * aspect
    return frustum( -w, w, -h, h, znear, zfar )
