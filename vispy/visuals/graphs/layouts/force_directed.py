# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Force-Directed Graph Layout
===========================

This module contains implementations for a force-directed layout, where each
edge is modelled like a spring, and the whole graph tries to reach a state
which requires the minimum energy.
"""

import numpy as np
from scipy.sparse import coo_matrix

from ..util import straight_line_vertices


class fruchterman_reingold:
    """
    Fruchterman-Reingold implementation adapted from NetworkX.
    """

    def __init__(self, optimal=None, iterations=50, pos=None):
        self.dim = 2
        self.optimal = optimal
        self.iterations = iterations
        self.num_nodes = None
        self.pos = pos

    def __call__(self, adjacency_mat, directed=False):
        if adjacency_mat.shape[0] != adjacency_mat[1]:
            raise ValueError("Adjacency matrix should be square.")

        self.num_nodes = adjacency_mat.shape[0]

        if self.num_nodes < 500:
            # Use the sparse solver
            self._sparse_fruchterman_reingold(adjacency_mat, directed)
        else:
            self._fruchterman_reingold(adjacency_mat, directed)

    def _fruchterman_reingold(self, adjacency_mat, directed=False):
        if self.optimal is None:
            self.optimal = 1 / np.sqrt(self.num_nodes)

        if self.pos is None:
            # Random initial positions
            pos = np.asarray(
                np.random.random((self.num_nodes, self.dim)),
                dtype=adjacency_mat.dtype
            )
        else:
            pos = self.pos.astype(adjacency_mat.dtype)

        # The initial "temperature"  is about .1 of domain area (=1x1)
        # this is the largest step allowed in the dynamics.
        t = 0.1

        # Simple cooling scheme.
        # Linearly step down by dt on each iteration so last iteration is
        # size dt.
        dt = t / float(self.iterations+1)
        delta = np.zeros(
            (pos.shape[0], pos.shape[0], pos.shape[1]),
            dtype=adjacency_mat.dtype
        )

        # The inscrutable (but fast) version
        # This is still O(V^2)
        # Could use multilevel methods to speed this up significantly
        for iteration in range(self.iterations):
            # Matrix of difference between points
            for i in range(pos.shape[1]):
                delta[:, :, i] = pos[:, i, None] - pos[:, i]

            # Distance between points
            distance = np.sqrt((delta**2).sum(axis=-1))
            # Enforce minimum distance of 0.01
            distance = np.where(distance < 0.01, 0.01, distance)
            # Displacement "force"
            displacement = np.transpose(
                np.transpose(delta) * (
                    self.optimal * self.optimal/distance**2 -
                    adjacency_mat*distance/self.optimal
                )
            ).sum(axis=1)

            # update positions
            length = np.sqrt((displacement**2).sum(axis=1))
            length = np.where(length < 0.01, 0.1, length)
            delta_pos = np.transpose(np.transpose(displacement)*t/length)
            pos += delta_pos

            # cool temperature
            t -= dt

            # Calculate edge vertices and arrows
            line_vertices, arrows = straight_line_vertices(adjacency_mat,
                                                           pos, directed)

            yield pos, line_vertices, arrows

    def _sparse_fruchterman_reingold(self, adjacency_mat, directed=False):
        # Optimal distance between nodes
        if self.optimal is None:
            self.optimal = 1 / np.sqrt(self.num_nodes)

        # make sure we have a LIst of Lists representation
        try:
            adjacency_mat = adjacency_mat.tolil()
        except:
            adjacency_mat = (coo_matrix(adjacency_mat)).tolil()

        if self.pos is None:
            # Random initial positions
            pos = np.asarray(
                np.random.random((self.num_nodes, self.dim)),
                dtype=adjacency_mat.dtype
            )
        else:
            pos = self.pos.astype(adjacency_mat.dtype)

        # The initial "temperature"  is about .1 of domain area (=1x1)
        # This is the largest step allowed in the dynamics.
        t = 0.1
        # Simple cooling scheme.
        # Linearly step down by dt on each iteration so last iteration is
        # size dt.
        dt = t / float(self.iterations+1)

        displacement = np.zeros((self.dim, self.num_nodes))
        for iteration in range(self.iterations):
            displacement *= 0
            # Loop over rows
            for i in range(adjacency_mat.shape[0]):
                # difference between this row's node position and all others
                delta = (pos[i]-pos).T
                # distance between points
                distance = np.sqrt((delta**2).sum(axis=0))
                # enforce minimum distance of 0.01
                distance = np.where(distance < 0.01, 0.01, distance)
                # the adjacency matrix row
                row = np.asarray(adjacency_mat.getrowview(i).toarray())
                # displacement "force"
                displacement[:, i] += (
                    delta * (
                        self.optimal *
                        self.optimal/distance**2 -
                        row*distance/self.optimal
                    )
                ).sum(axis=1)

            # Update positions
            length = np.sqrt((displacement**2).sum(axis=0))
            length = np.where(length < 0.01, 0.1, length)
            pos += (displacement*t/length).T

            # Cool temperature
            t -= dt

            # Calculate line vertices
            line_vertices, arrows = straight_line_vertices(adjacency_mat,
                                                           pos, directed)

            yield pos, line_vertices, arrows
