# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Graph Visual
============

This visual can be used to visualise graphs or networks.
"""

import itertools

import numpy as np

from ..visual import CompoundVisual
from ..line import ArrowVisual
from ..markers import MarkersVisual


class GraphVisual(CompoundVisual):
    """Visual for displaying graphs or networks.

    See Also
    --------
    ArrowVisual, MarkersVisual

    """

    _arrow_attributes = ('arrow_type', 'arrow_size')
    _arrow_kwargs = ('line_color', 'line_width')
    _node_kwargs = ('node_symbol', 'node_size', 'edge_color', 'face_color',
                    'edge_width')

    _arrow_kw_trans = dict(line_color='color', line_width='width')
    _node_kw_trans = dict(node_symbol='symbol', node_size='size')

    def __init__(self, adjacency_mat=None, directed=False, line_color=None,
                 line_width=None, arrow_type=None, arrow_size=None,
                 node_symbol=None, node_size=None, edge_color=None,
                 face_color=None, edge_width=None, layout=None):

        self._edges = ArrowVisual(method='gl', connect='segments')
        self._nodes = MarkersVisual()

        self._adjacency_mat = None
        self._layout = None
        self._layout_iter = None
        self.layout = layout
        self._directed = directed
        self.directed = directed

        CompoundVisual.__init__(self, [self._edges, self._nodes])

        self.set_data(adjacency_mat, line_color=line_color,
                      line_width=line_width, arrow_type=arrow_type,
                      arrow_size=arrow_size, node_symbol=node_symbol,
                      node_size=node_size, edge_color=edge_color,
                      face_color=face_color, edge_width=edge_width)

    @property
    def adjacency_matrix(self):
        return self._adjacency_mat

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, value):
        self._layout = value

    @property
    def directed(self):
        return self._directed

    @directed.setter
    def directed(self, value):
        self._directed = bool(value)

    def animate_layout(self):
        if self._layout_iter is None:
            if self._adjacency_mat is None:
                raise ValueError("No adjacency matrix set yet. An adjacency "
                                 "matrix is required to calculate the layout.")

            self._layout_iter = iter(self._layout(self._adjacency_mat))

        try:
            node_vertices, line_vertices = next(self._layout_iter)
        except StopIteration:
            return False

        self._nodes.set_data(pos=node_vertices)

        if self._directed:
            # TODO: Fix arrows
            pass

        self._edges.set_data(pos=line_vertices)

        return True

    def final_layout(self):
        if self._layout_iter is None:
            if self._adjacency_mat is None:
                raise ValueError("No adjacency matrix set yet. An adjacency "
                                 "matrix is required to calculate the layout.")

            self._layout_iter = iter(self._layout(self._adjacency_mat))

        node_vertices, line_vertices = None
        for node_vertices, line_vertices in self._layout_iter:
            pass

        self._nodes.set_data(pos=node_vertices)
        self._edges.set_data(pos=line_vertices)

    def set_data(self, adjacency_mat=None, **kwargs):
        line_vertices = None
        arrows = None
        node_coords = None

        if adjacency_mat is not None:
            if adjacency_mat.shape[0] != adjacency_mat.shape[1]:
                raise ValueError("Adjacency matrix should be square.")

            # Randomly place nodes, visual coordinate system is between -1 and 1
            num_nodes = adjacency_mat.shape[0]
            node_coords = np.random.rand(num_nodes, 2)

            line_vertices = []
            arrows = []
            for edge in itertools.combinations(range(num_nodes), 2):
                reverse = (edge[1], edge[0])

                if adjacency_mat[edge] == 1 or adjacency_mat[reverse] == 1:
                    line_vertices.extend([node_coords[edge[0]],
                                          node_coords[edge[1]]])

                # Check if edge is directed, and if so, add an arrow head
                if adjacency_mat[edge] == 1 and adjacency_mat[reverse] == 0:
                    arrows.extend([
                        node_coords[edge[0]], node_coords[edge[1]]
                    ])

                elif adjacency_mat[edge] == 0 and adjacency_mat[reverse] == 1:
                    arrows.extend([
                        node_coords[reverse[0]], node_coords[reverse[1]]
                    ])

            line_vertices = np.array(line_vertices)
            arrows = np.array(arrows).reshape((len(arrows)/2, 4))

        for k in self._arrow_attributes:
            if k in kwargs:
                translated = (self._arrow_kw_trans[k] if k in
                              self._arrow_kw_trans else k)

                setattr(self._edges, translated, kwargs.pop(k))

        arrow_kwargs = {}
        for k in self._arrow_kwargs:
            if k in kwargs:
                translated = (self._arrow_kw_trans[k] if k in
                              self._arrow_kw_trans else k)

                arrow_kwargs[translated] = kwargs.pop(k)

        self._edges.set_data(pos=line_vertices, arrows=arrows, **arrow_kwargs)

        node_kwargs = {}
        for k in self._node_kwargs:
            if k in kwargs:
                translated = (self._node_kw_trans[k] if k in
                              self._node_kw_trans else k)

                node_kwargs[translated] = kwargs.pop(k)

        self._nodes.set_data(pos=node_coords, **node_kwargs)

        if len(kwargs) > 0:
            raise TypeError(
                "{}.set_data() got invalid keyword arguments: {}".format(
                    self.__class__.__name__,
                    kwargs.keys()
                )
            )
