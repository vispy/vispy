# -*- coding: utf-8 -*-

# A Cython implementation of the "eight-points signed sequential Euclidean
# distance transform algorithm" (8SSEDT)

import numpy as np
cimport numpy as np
from libc.math cimport sqrt
cimport cython

__all__ = ['_get_distance_field']

dtype = np.float32
dtype_c = np.complex64
ctypedef np.float32_t DTYPE_t
ctypedef np.complex64_t DTYPE_ct

cdef DTYPE_ct MAX_VAL = (1e6 + 1e6j)


@cython.boundscheck(False)  # designed to stay within bounds
@cython.wraparound(False)  # we don't use negative indexing
def _calc_distance_field(np.ndarray[DTYPE_t, ndim=2] pixels,
                         int w, int h, DTYPE_t sp_f):
    # initialize grids
    cdef np.ndarray[DTYPE_ct, ndim=2] g0 = np.zeros((h, w), dtype_c)
    cdef np.ndarray[DTYPE_ct, ndim=2] g1 = np.zeros((h, w), dtype_c)
    cdef Py_ssize_t y, x
    for y in range(h):
        g0[y, 0] = MAX_VAL
        g0[y, w-1] = MAX_VAL
        g1[y, 0] = MAX_VAL
        g1[y, w-1] = MAX_VAL
        for x in range(1, w-1):
            if pixels[y, x] > 0:
                g0[y, x] = MAX_VAL
            if pixels[y, x] < 1:
                g1[y, x] = MAX_VAL
    for x in range(w):
        g0[0, x] = MAX_VAL
        g0[h-1, x] = MAX_VAL
        g1[0, x] = MAX_VAL
        g1[h-1, x] = MAX_VAL

    # Propagate grids
    _propagate(g0)
    _propagate(g1)

    # Subtracting and normalizing
    cdef DTYPE_t r_sp_f_2 = 1. / (sp_f * 2.)
    for y in range(1, h-1):
        for x in range(1, w-1):
            pixels[y, x] = sqrt(dist(g0[y, x])) - sqrt(dist(g1[y, x]))
            if pixels[y, x] < 0:
                pixels[y, x] = (pixels[y, x] + sp_f) * r_sp_f_2
            else:
                pixels[y, x] = 0.5 + pixels[y, x] * r_sp_f_2
            pixels[y, x] = max(min(pixels[y, x], 1), 0)


@cython.boundscheck(False)  # designed to stay within bounds
@cython.wraparound(False)  # we don't use negative indexing
cdef Py_ssize_t compare(DTYPE_ct *cell, DTYPE_ct xy, DTYPE_t *current):
    cdef DTYPE_t val = dist(xy)
    if val < current[0]:
        cell[0] = xy
        current[0] = val


@cython.boundscheck(False)  # designed to stay within bounds
@cython.wraparound(False)  # we don't use negative indexing
cdef DTYPE_t dist(DTYPE_ct val):
    return val.real*val.real + val.imag*val.imag


@cython.boundscheck(False)  # designed to stay within bounds
@cython.wraparound(False)  # we don't use negative indexing
cdef void _propagate(np.ndarray[DTYPE_ct, ndim=2] grid):
    cdef Py_ssize_t height = grid.shape[0]
    cdef Py_ssize_t width = grid.shape[1]
    cdef Py_ssize_t y, x
    cdef DTYPE_t current
    cdef DTYPE_ct a0=-1, a1=-1j, a2=-1-1j, a3=1-1j
    cdef DTYPE_ct b0=1
    cdef DTYPE_ct c0=1, c1=1j, c2=-1+1j, c3=1+1j
    cdef DTYPE_ct d0=-1
    height -= 1
    width -= 1
    for y in range(1, height):
        for x in range(1, width):
            current = dist(grid[y, x])
            # (-1, +0), (+0, -1), (-1, -1), (+1, -1)
            compare(&grid[y, x], grid[y, x-1] + a0, &current)
            compare(&grid[y, x], grid[y-1, x] + a1, &current)
            compare(&grid[y, x], grid[y-1, x-1] + a2, &current)
            compare(&grid[y, x], grid[y-1, x+1] + a3, &current)
        for x in range(width - 1, 0, -1):
            current = dist(grid[y, x])
            # (+1, +0)
            compare(&grid[y, x], grid[y, x+1] + b0, &current)
    for y in range(height - 1, 0, -1):
        for x in range(width - 1, 0, -1):
            current = dist(grid[y, x])
            # (+1, +0), (+0, +1), (-1, +1), (+1, +1)
            compare(&grid[y, x], grid[y, x+1] + c0, &current)
            compare(&grid[y, x], grid[y+1, x] + c1, &current)
            compare(&grid[y, x], grid[y+1, x-1] + c2, &current)
            compare(&grid[y, x], grid[y+1, x+1] + c3, &current)
        for x in range(1, width):
            current = dist(grid[y, x])
            # (-1, +0)
            compare(&grid[y, x], grid[y, x-1] + d0, &current)
