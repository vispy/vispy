# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Graph Visual
============

This visual can be used to visualise graphs or networks.
"""

from collections import defaultdict

from .visual import CompoundVisual
from .line import ArrowVisual
from .markers import MarkersVisual


class GraphVisual(CompoundVisual):
    """Visual for displaying graphs or networks.

    See Also
    --------
    ArrowVisual, MarkersVisual

    """

    _arrow_kwargs = ('line_color', 'line_width', 'arrow_type')
    _node_kwargs = ('node_symbol', 'node_size', 'edge_color', 'face_color',
                    'edge_width')

    _arrow_kw_trans = dict(line_color='color', line_width='width')
    _node_kw_trans = dict(node_symbol='symbol', node_size='size')

    def __init__(self, connectivity=None, line_color=None, line_width=None,
                 arrow_type=None, node_symbol=None, node_size=None,
                 edge_color=None, face_color=None, edge_width=None):

        self._edges = ArrowVisual(method='gl', antialias=True)
        self._nodes = MarkersVisual()

        self._connectivity = None

        CompoundVisual.__init__(self, [self._edges, self._nodes])

        self.set_data(connectivity, line_color=line_color,
                      line_width=line_width, arrow_type=arrow_type,
                      node_symbol=node_symbol, node_size=node_size,
                      edge_color=edge_color, face_color=face_color,
                      edge_width=edge_width)

    def set_data(self, connectivity, **kwargs):
        # TODO: Generate vertex data for markers and edges
        self._connectivity = connectivity

        arrow_kwargs = {}
        for k in self._arrow_kwargs:
            if k in kwargs:
                translated = (self._arrow_kw_trans[k] if k in
                              self._arrow_kw_trans else k)

                arrow_kwargs[translated] = kwargs.pop(k)

        self._edges.set_data(**arrow_kwargs)

        node_kwargs = {}
        for k in self._node_kwargs:
            if k in kwargs:
                translated = (self._node_kw_trans[k] if k in
                              self._node_kw_trans else k)

                node_kwargs[translated] = kwargs.pop(k)

        self._nodes.set_data(**node_kwargs)

        if len(kwargs) > 0:
            raise TypeError(
                "{}.set_data() got invalid keyword arguments: {}".format(
                    self.__class__.__name__,
                    kwargs.keys()
                )
            )
