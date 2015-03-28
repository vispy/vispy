# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np


def compact(vertices, indices, tolerance=1e-3):
    """ Compact vertices and indices within given tolerance """

    # Transform vertices into a structured array for np.unique to work
    n = len(vertices)
    V = np.zeros(n, dtype=[("pos", np.float32, 3)])
    V["pos"][:, 0] = vertices[:, 0]
    V["pos"][:, 1] = vertices[:, 1]
    V["pos"][:, 2] = vertices[:, 2]

    epsilon = 1e-3
    decimals = int(np.log(epsilon)/np.log(1/10.))

    # Round all vertices within given decimals
    V_ = np.zeros_like(V)
    X = V["pos"][:, 0].round(decimals=decimals)
    X[np.where(abs(X) < epsilon)] = 0

    V_["pos"][:, 0] = X
    Y = V["pos"][:, 1].round(decimals=decimals)
    Y[np.where(abs(Y) < epsilon)] = 0
    V_["pos"][:, 1] = Y

    Z = V["pos"][:, 2].round(decimals=decimals)
    Z[np.where(abs(Z) < epsilon)] = 0
    V_["pos"][:, 2] = Z

    # Find the unique vertices AND the mapping
    U, RI = np.unique(V_, return_inverse=True)

    # Translate indices from original vertices into the reduced set (U)
    indices = indices.ravel()
    I_ = indices.copy().ravel()
    for i in range(len(indices)):
        I_[i] = RI[indices[i]]
    I_ = I_.reshape(len(indices)/3, 3)

    # Return reduced vertices set, transalted indices and mapping that allows
    # to go from U to V
    return U.view(np.float32).reshape(len(U), 3), I_, RI


def normals(vertices, indices):
    """
    Compute normals over a triangulated surface

    Parameters
    ----------

    vertices : ndarray (n,3)
        triangles vertices

    indices : ndarray (p,3)
        triangles indices
    """

    # Compact similar vertices
    vertices, indices, mapping = compact(vertices, indices)

    T = vertices[indices]
    N = np.cross(T[:, 1] - T[:, 0], T[:, 2]-T[:, 0])
    L = np.sqrt(np.sum(N * N, axis=1))
    L[L == 0] = 1.0  # prevent divide-by-zero
    N /= L[:, np.newaxis]
    normals = np.zeros_like(vertices)
    normals[indices[:, 0]] += N
    normals[indices[:, 1]] += N
    normals[indices[:, 2]] += N
    L = np.sqrt(np.sum(normals*normals, axis=1))
    L[L == 0] = 1.0
    normals /= L[:, np.newaxis]

    return normals[mapping]
