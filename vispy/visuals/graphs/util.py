# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Graph utilities
===============

A module containing several graph utility functions.
"""

import itertools

import numpy as np

try:
    from scipy.sparse import issparse
except ImportError:
    def issparse(*args, **kwargs):
        return False


def get_edges(adjacency_mat):
    if issparse(adjacency_mat):
        func = _sparse_get_edges
    else:
        func = _get_edges

    for result in func(adjacency_mat):
        yield result


def _sparse_get_edges(adjacency_mat):
    coo_mat = adjacency_mat.tocoo()
    return zip(coo_mat.row, coo_mat.col)


def _get_edges(adjacency_mat):
    i, j = np.where(adjacency_mat)

    return zip(i, j)


def straight_line_vertices(adjacency_mat, node_coords, directed=False):
    """
    Generate the vertices for straight lines between nodes.

    If it is a directed graph, it also generates the vertices which can be
    passed to an :class:`ArrowVisual`.

    Parameters
    ----------
    adjacency_mat : array
        The adjacency matrix of the graph
    node_coords : array
        The current coordinates of all nodes in the graph
    directed : bool
        Wether the graph is directed. If this is true it will also generate
        the vertices for arrows which can be passed to :class:`ArrowVisual`.

    Returns
    -------
    vertices : tuple
        Returns a tuple containing containing (`line_vertices`,
        `arrow_vertices`)
    """

    if (not issparse(adjacency_mat) and not isinstance(adjacency_mat,
                                                       np.ndarray)):
        adjacency_mat = np.array(adjacency_mat, float)

    if (adjacency_mat.ndim != 2 or adjacency_mat.shape[0] !=
            adjacency_mat.shape[1]):
        raise ValueError("Adjacency matrix should be square.")

    line_vertices = []
    arrows = []

    for edge in get_edges(adjacency_mat):
        reverse = (edge[1], edge[0])

        if adjacency_mat[edge] == 1 or adjacency_mat[reverse] == 1:
            line_vertices.extend([node_coords[edge[0]],
                                  node_coords[edge[1]]])

        if directed:
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
    Changes `pos` in place.
    """

    pos -= pos.min(axis=0)
    pos *= scale / pos.max()

    return pos
