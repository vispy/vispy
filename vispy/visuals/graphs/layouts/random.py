# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Random Graph Layout
====================

This layout positions the nodes at random
"""

import numpy as np

from ..util import _straight_line_vertices, issparse


def random(adjacency_mat, directed=False, random_state=None):
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
    random_state : instance of RandomState | int | None
        Random state to use. Can be None to use ``np.random``.

    Yields
    ------
    (node_vertices, line_vertices, arrow_vertices) : tuple
        Yields the node and line vertices in a tuple. This layout only yields a
        single time, and has no builtin animation
    """
    if random_state is None:
        random_state = np.random
    elif not isinstance(random_state, np.random.RandomState):
        random_state = np.random.RandomState(random_state)

    if issparse(adjacency_mat):
        adjacency_mat = adjacency_mat.tocoo()

    # Randomly place nodes, visual coordinate system is between 0 and 1
    num_nodes = adjacency_mat.shape[0]
    node_coords = random_state.rand(num_nodes, 2)

    line_vertices, arrows = _straight_line_vertices(adjacency_mat,
                                                    node_coords, directed)

    yield node_coords, line_vertices, arrows
