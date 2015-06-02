

from __future__ import division

import numpy as np



def create_implicit_mesh(xs, ys, zs):
    '''Generate vertices and indices for an implicitly connected mesh.

    The intention is that this makes it simple to generate a mesh
    from meshgrid data.

    Parameters
    ----------
    xs : ndarray
        A 2d array of x coordinates for the vertices of the mesh. Must
        have the same dimensions as ys and zs.
    ys : ndarray
        A 2d array of y coordinates for the vertices of the mesh. Must
        have the same dimensions as xs and zs.
    zs : ndarray
        A 2d array of z coordinates for the vertices of the mesh. Must
        have the same dimensions as xs and ys.

    Returns
    -------
    vertices : ndarray
        The array of vertices in the mesh.
    indices : ndarray
        The array of indices for the mesh.
    '''

    shape = xs.shape
    length = shape[0] * shape[1]

    vertices = np.zeros((length, 3))
    
    vertices[:, 0] = xs.reshape(length)
    vertices[:, 1] = ys.reshape(length)
    vertices[:, 2] = zs.reshape(length)


    # indices = np.resize(
    #     [0, 1, 1 + shape[0], 0, 0 + shape[0], 1 + shape[0]],
    basic_indices = np.array([0, 1, 1 + shape[1], 0,
                             0 + shape[1], 1 + shape[1]])

    indices_length = (shape[0] - 1) * (shape[1] - 1) * 6
    indices = np.zeros(indices_length, dtype=np.uint32)
    index = 0
    for i in range(shape[0] - 1):
        ival = i * shape[1]
        for j in range(shape[1] - 1):
            val = ival + j
            indices[index*6:index*6 + 6] = basic_indices + val
            index += 1

    return vertices, indices
                
    
