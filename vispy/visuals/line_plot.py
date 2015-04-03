# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np

from .line import LineVisual
from .markers import MarkersVisual
from .visual import Visual


class LinePlotVisual(Visual):
    """Visual displaying a plot line with optional markers.

    Parameters
    ----------
    data : array-like
        Arguments can be passed as ``(Y,)``, ``(X, Y)`` or
        ``np.array((X, Y))``.
    color : instance of Color
        Color of the line.
    symbol : str
        Marker symbol to use.
    line_kind : str
        Kind of line to draw. For now, only solid lines (``'-'``)
        are supported.
    width : float
        Line width.
    marker_size : float
        Marker size. If `size == 0` markers will not be shown.
    edge_color : instance of Color
        Color of the marker edge.
    face_color : instance of Color
        Color of the marker face.
    edge_width : float
        Edge width of the marker.
    connect : str | array
        See LineVisual.
    **kwargs : keyword arguments
        Argements to pass to the super class.

    Examples
    --------
    All of these syntaxes will work:

        >>> LinePlotVisual(y_vals)
        >>> LinePlotVisual(x_vals, y_vals)
        >>> LinePlotVisual(xy_vals)

    See also
    --------
    LineVisual, MarkersVisual, marker_types
    """
    _line_kwargs = ('color', 'width', 'connect')
    _marker_kwargs = ('edge_color', 'face_color', 'edge_width',
                      'marker_size', 'symbol')
    _kw_trans = dict(marker_size='size')

    def __init__(self, data, color='k', symbol='o', line_kind='-',
                 width=1., marker_size=10., edge_color='k', face_color='w',
                 edge_width=1., connect='strip', **kwargs):
        Visual.__init__(self, **kwargs)
        if line_kind != '-':
            raise ValueError('Only solid lines currently supported')
        self._line = LineVisual()
        self._markers = MarkersVisual()
        self.set_data(data, color=color, symbol=symbol,
                      width=width, marker_size=marker_size,
                      edge_color=edge_color, face_color=face_color,
                      edge_width=edge_width, connect=connect)

    def set_data(self, data, **kwargs):
        args = [np.array(x) for x in data]

        if len(args) == 1:
            arg = args[0]
            if arg.ndim == 2:
                # xy array already provided
                pos = arg
            elif arg.ndim == 1:
                # only y supplied, generate arange x
                pos = np.empty((len(arg), 2), dtype=np.float32)
                pos[:, 1] = arg
                pos[:, 0] = np.arange(len(arg))
            else:
                raise TypeError("Invalid argument: array must have ndim "
                                "<= 2.")
        elif len(args) == 2:
            pos = np.concatenate([args[0][:, np.newaxis],
                                  args[1][:, np.newaxis]], axis=1)
        # if args are empty, don't modify position
        elif len(args) == 0:
            pos = self._line.pos

            # if both args and keywords are zero, then there is no
            # point in calling this function.
            if len(kwargs) == 0:
                raise TypeError("neither line points nor line properties"
                                "are provided")
        else:
            raise TypeError("Too many positional arguments given (max is 2).")

        # todo: have both sub-visuals share the same buffers.
        line_kwargs = {}
        for k in self._line_kwargs:
            if k in kwargs:
                k_ = self._kw_trans[k] if k in self._kw_trans else k
                line_kwargs[k] = kwargs.pop(k_)
        self._line.set_data(pos=pos, **line_kwargs)
        marker_kwargs = {}
        for k in self._marker_kwargs:
            if k in kwargs:
                k_ = self._kw_trans[k] if k in self._kw_trans else k
                marker_kwargs[k_] = kwargs.pop(k)
        self._markers.set_data(pos=pos, **marker_kwargs)
        if len(kwargs) > 0:
            raise TypeError("Invalid keyword arguments: %s" % kwargs.keys())

    def bounds(self, mode, axis):
        return self._line.bounds(mode, axis)

    def draw(self, transforms):
        for v in self._line, self._markers:
            v.draw(transforms)
