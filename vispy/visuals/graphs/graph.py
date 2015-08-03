# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Graph Visual
============

This visual can be used to visualise graphs or networks.
"""

from ..visual import CompoundVisual
from ..line import ArrowVisual
from ..markers import MarkersVisual
from . import layouts


_layouts_map = {
    'random': layouts.random,
    'circular': layouts.circular
}

AVAILABLE_LAYOUTS = _layouts_map.keys()


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

    def __init__(self, adjacency_mat=None, directed=False, layout=None,
                 animate=False, line_color=None, line_width=None,
                 arrow_type=None, arrow_size=None, node_symbol=None,
                 node_size=None, edge_color=None, face_color=None,
                 edge_width=None):

        self._edges = ArrowVisual(method='gl', connect='segments')
        self._nodes = MarkersVisual()

        self._arrow_data = {}
        self._node_data = {}

        self._adjacency_mat = None

        self._layout = None
        self._layout_iter = None
        self.layout = layout

        self._directed = directed
        self.directed = directed

        self._animate = False
        self.animate = animate

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
        if type(value) == str:
            if value not in AVAILABLE_LAYOUTS:
                raise ValueError(
                    "Invalid graph layout '{}'. Should be one of {}.".format(
                        value,
                        ", ".join(AVAILABLE_LAYOUTS)
                    )
                )

            self._layout = _layouts_map[value]
        else:
            assert callable(value)
            self._layout = value

    @property
    def directed(self):
        return self._directed

    @directed.setter
    def directed(self, value):
        self._directed = bool(value)

    @property
    def animate(self):
        return self._animate

    @animate.setter
    def animate(self, value):
        self._animate = bool(value)

    def animate_layout(self):
        if self._layout_iter is None:
            if self._adjacency_mat is None:
                raise ValueError("No adjacency matrix set yet. An adjacency "
                                 "matrix is required to calculate the layout.")

            self._layout_iter = iter(self._layout(self._adjacency_mat,
                                                  self._directed))

        try:
            node_vertices, line_vertices, arrows = next(self._layout_iter)
        except StopIteration:
            return False

        self._nodes.set_data(pos=node_vertices, **self._node_data)
        self._edges.set_data(pos=line_vertices, arrows=arrows,
                             **self._arrow_data)

        return True

    def set_final_layout(self):
        if self._layout_iter is None:
            if self._adjacency_mat is None:
                raise ValueError("No adjacency matrix set yet. An adjacency "
                                 "matrix is required to calculate the layout.")

            self._layout_iter = iter(self._layout(self._adjacency_mat,
                                                  self._directed))

        # Calculate the final position of the nodes and lines
        node_vertices = None
        line_vertices = None
        arrows = None
        for node_vertices, line_vertices, arrows in self._layout_iter:
            pass

        self._nodes.set_data(pos=node_vertices, **self._node_data)
        self._edges.set_data(pos=line_vertices, arrows=arrows,
                             **self._arrow_data)

    def set_data(self, adjacency_mat=None, **kwargs):
        if adjacency_mat is not None:
            if adjacency_mat.shape[0] != adjacency_mat.shape[1]:
                raise ValueError("Adjacency matrix should be square.")

            self._adjacency_mat = adjacency_mat

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

        node_kwargs = {}
        for k in self._node_kwargs:
            if k in kwargs:
                translated = (self._node_kw_trans[k] if k in
                              self._node_kw_trans else k)

                node_kwargs[translated] = kwargs.pop(k)

        if len(kwargs) > 0:
            raise TypeError(
                "{}.set_data() got invalid keyword arguments: {}".format(
                    self.__class__.__name__,
                    kwargs.keys()
                )
            )

        # The actual data is set in GraphVisual.animate_layout or
        # GraphVisual.set_final_layout
        self._arrow_data = arrow_kwargs
        self._node_data = node_kwargs

        if not self._animate:
            self.set_final_layout()
