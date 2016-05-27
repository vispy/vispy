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
from ...ext.six import string_types


class GraphVisual(CompoundVisual):
    """Visual for displaying graphs or networks.

    Parameters
    ----------
    adjacency_mat : array or sparse
        The adjacency matrix of the graph.
    directed : bool
        Whether the graph is directed or not. If True, then this visual will
        draw arrows for the directed edges.
    layout : str
        They layout to use.
    animate : bool
        Whether or not to animate.
    line_color : str or :class:`vispy.color.colormap.ColorMap`
        The color to use for the edges.
    line_width : number
        The edge thickness.
    arrow_type : str
        The kind of arrow head to use. See :class:`vispy.visuals.ArrowHead`
        for more information.
    arrow_size : number
        The size of the arrow head.
    node_symbol : string
        The marker to use for nodes. See
        :class:`vispy.visuals.MarkersVisual` for more information.
    node_size : number
        The size of the node
    border_color : str or :class:`vispy.color.colormap.ColorMap`
        The border color for nodes.
    face_color : str or :class:`vispy.color.colormap.ColorMap`
        The face color for nodes.
    border_width : number
        The border size for nodes.

    See Also
    --------
    ArrowVisual, MarkersVisual

    """

    _arrow_attributes = ('arrow_type', 'arrow_size')
    _arrow_kwargs = ('line_color', 'line_width')
    _node_kwargs = ('node_symbol', 'node_size', 'border_color', 'face_color',
                    'border_width')

    _arrow_kw_trans = dict(line_color='color', line_width='width')
    _node_kw_trans = dict(node_symbol='symbol', node_size='size',
                          border_color='edge_color', border_width='edge_width')

    def __init__(self, adjacency_mat=None, directed=False, layout=None,
                 animate=False, line_color=None, line_width=None,
                 arrow_type=None, arrow_size=None, node_symbol=None,
                 node_size=None, border_color=None, face_color=None,
                 border_width=None):

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
                      node_size=node_size, border_color=border_color,
                      face_color=face_color, border_width=border_width)

    @property
    def adjacency_matrix(self):
        return self._adjacency_mat

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, value):
        if isinstance(value, string_types):
            self._layout = layouts.get_layout(value)
        else:
            assert callable(value)
            self._layout = value

        self._layout_iter = None

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
            return True

        self._nodes.set_data(pos=node_vertices, **self._node_data)
        self._edges.set_data(pos=line_vertices, arrows=arrows,
                             **self._arrow_data)

        return False

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

    def reset_layout(self):
        self._layout_iter = None

    def set_data(self, adjacency_mat=None, **kwargs):
        """Set the data

        Parameters
        ----------
        adjacency_mat : ndarray | None
            The adjacency matrix.
        **kwargs : dict
            Keyword arguments to pass to the arrows.
        """
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
            raise TypeError("%s.set_data() got invalid keyword arguments: %S"
                            % (self.__class__.__name__, list(kwargs.keys())))

        # The actual data is set in GraphVisual.animate_layout or
        # GraphVisual.set_final_layout
        self._arrow_data = arrow_kwargs
        self._node_data = node_kwargs

        if not self._animate:
            self.set_final_layout()
