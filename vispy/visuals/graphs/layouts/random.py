# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Random Graph Layout
====================

This layout positions the nodes at random
"""

import numpy as np

from ..util import _straight_line_vertices, issparse


def random(adjacency_mat, directed=False):
    """
    Place the graph nodes at random places.

    Parameters
    ----------
    adjacency_mat : matrix or sparse
        The graph adjacency matrix
    directed : bool
        Whether the graph is directed. If this is True, is will also
        generate the vertices for arrows, which can be passed to an
        ArrowVisual.

    Yields
    ------
    (node_vertices, line_vertices, arrow_vertices) : tuple
        Yields the node and line vertices in a tuple. This layout only yields a
        single time, and has no builtin animation
    """

    if issparse(adjacency_mat):
        adjacency_mat = adjacency_mat.tocoo()

    # Randomly place nodes, visual coordinate system is between 0 and 1
    num_nodes = adjacency_mat.shape[0]
    node_coords = np.random.rand(num_nodes, 2)

    line_vertices, arrows = _straight_line_vertices(adjacency_mat,
                                                    node_coords, directed)

    yield node_coords, line_vertices, arrows
