# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Random Graph Layout
====================

This layout positions the nodes at random
"""

import numpy as np

from ..util import _straight_line_vertices


def random(adjacency_mat, directed=False):
    if adjacency_mat.shape[0] != adjacency_mat.shape[1]:
        raise ValueError("Adjacency matrix should be square.")

    # Randomly place nodes, visual coordinate system is between 0 and 1
    num_nodes = adjacency_mat.shape[0]
    node_coords = np.random.rand(num_nodes, 2)

    line_vertices, arrows = _straight_line_vertices(adjacency_mat,
                                                   node_coords, directed)

    yield node_coords, line_vertices, arrows
