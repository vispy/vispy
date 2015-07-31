# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Circular Layout
===============

This module contains several graph layouts which rely heavily on circles.
"""

import itertools

import numpy as np


def circular(adjacency_mat):
    """Places all nodes on a single circle.

    Parameters
    ----------
    adjacency_mat : matrix
        The graph adjacency matrix

    Yields
    ------
    (node_vertices, line_vertices) : tuple
        Yields the node and line vertices in a tuple. This layout only yields a
        single time, and has no builtin animation
    """

    if adjacency_mat.shape[0] != adjacency_mat.shape[1]:
        raise ValueError("Adjacency matrix should be square.")

    num_nodes = adjacency_mat.shape[0]

    t = np.arange(0, 2.0*np.pi, 2.0*np.pi/num_nodes, dtype=np.float32)

    # Visual coordinate system is between 0 and 1, so generate a circle with
    # radius 0.5 and center it at the point (0.5, 0.5).
    node_coords = np.transpose(0.5 * np.array([np.cos(t), np.sin(t)]) + 0.5)

    line_vertices = []
    for edge in itertools.combinations(range(num_nodes), 2):
        reverse = (edge[1], edge[0])

        if adjacency_mat[edge] == 1 or adjacency_mat[reverse] == 1:
            line_vertices.extend([node_coords[edge[0]],
                                  node_coords[edge[1]]])

    yield node_coords, np.array(line_vertices)




