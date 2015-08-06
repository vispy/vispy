# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Graph utilities
===============

A module containing several graph utility functions
"""

import itertools

import numpy as np


def straight_line_vertices(adjacency_mat, node_coords, directed=False):
    if adjacency_mat.shape[0] != adjacency_mat.shape[1]:
        raise ValueError("Adjacency matrix should be square.")

    num_nodes = adjacency_mat.shape[0]

    line_vertices = []
    arrows = []
    for edge in itertools.combinations(range(num_nodes), 2):
        reverse = (edge[1], edge[0])

        if adjacency_mat[edge] == 1 or adjacency_mat[reverse] == 1:
            line_vertices.extend([node_coords[edge[0]],
                                  node_coords[edge[1]]])

        if directed:
            # TODO: This can probably be vectorized
            if adjacency_mat[edge] == 1 and adjacency_mat[reverse] == 0:
                arrows.extend([
                    node_coords[edge[0]],
                    node_coords[edge[1]]
                ])
            elif adjacency_mat[edge] == 0 and adjacency_mat[reverse] == 0:
                arrows.extend([
                    node_coords[reverse[0]],
                    node_coords[reverse[1]]
                ])

    line_vertices = np.array(line_vertices)
    arrows = np.array(arrows).reshape((len(arrows)/2, 4))

    return line_vertices, arrows


def rescale_layout(pos, scale=1):
    """
    Normalize the given coordinate list to the range [0, `scale`].

    Parameters
    ----------
    pos : array
        Coordinate list
    scale : number
        The upperbound value for the coordinates range

    Returns
    -------
    pos : array
        The rescaled (normalized) coordinates in the range [0, `scale`].

    Notes
    -----
    Adapted from NetworkX.
    """

    # shift origin to (0,0)
    lim = 0 # max coordinate for all axes
    for i in range(pos.shape[1]):
        pos[:, i] -= pos[:, i].min()
        lim = max(pos[:, i].max(), lim)

    # rescale to (0,scale) in all directions, preserves aspect
    for i in range(pos.shape[1]):
        pos[:, i] *= scale/lim

    return pos
