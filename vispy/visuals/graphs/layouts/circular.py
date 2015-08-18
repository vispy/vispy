# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Circular Layout
===============

This module contains several graph layouts which rely heavily on circles.
"""

import numpy as np

from ..util import _straight_line_vertices, issparse


def circular(adjacency_mat, directed=False):
    """Places all nodes on a single circle.

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

    num_nodes = adjacency_mat.shape[0]

    t = np.linspace(0, 2 * np.pi, num_nodes, endpoint=False, dtype=np.float32)

    # Visual coordinate system is between 0 and 1, so generate a circle with
    # radius 0.5 and center it at the point (0.5, 0.5).
    node_coords = (0.5 * np.array([np.cos(t), np.sin(t)]) + 0.5).T

    line_vertices, arrows = _straight_line_vertices(adjacency_mat,
                                                    node_coords, directed)

    yield node_coords, line_vertices, arrows
