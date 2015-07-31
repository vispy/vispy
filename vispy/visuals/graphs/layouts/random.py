# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Random Graph Layout
====================

This layout positions the nodes at random
"""

import itertools

import numpy as np


def random(adjacency_mat):
    if adjacency_mat.shape[0] != adjacency_mat.shape[1]:
        raise ValueError("Adjacency matrix should be square.")

    # Randomly place nodes, visual coordinate system is between 0 and 1
    num_nodes = adjacency_mat.shape[0]
    node_coords = np.random.rand(num_nodes, 2)

    line_vertices = []
    for edge in itertools.combinations(range(num_nodes), 2):
        reverse = (edge[1], edge[0])

        if adjacency_mat[edge] == 1 or adjacency_mat[reverse] == 1:
            line_vertices.extend([node_coords[edge[0]],
                                  node_coords[edge[1]]])

    # Random layout does not have intermediate results, so this yield is more
    # like a return
    yield node_coords, np.array(line_vertices)


