# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np

from .line import LineVisual
from .markers import MarkersVisual
from .visual import CompoundVisual


class LinePlotVisual(CompoundVisual):
    """Visual displaying a plot line with optional markers.

    Parameters
    ----------
    data : array-like
        Arguments can be passed as ``(Y,)``, ``(X, Y)``, ``(X, Y, Z)`` or
        ``np.array((X, Y))``, ``np.array((X, Y, Z))``.
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
    LineVisual, MarkersVisual
    """

    _line_kwargs = ('color', 'width', 'connect')
    _marker_kwargs = ('edge_color', 'face_color', 'edge_width',
                      'marker_size', 'symbol')
    _valid_kwargs = set(_line_kwargs).union(set(_marker_kwargs))
    _kw_trans = dict(marker_size='size')

    def __init__(self, data=None, color='k', symbol=None, line_kind='-',
                 width=1., marker_size=10., edge_color='k', face_color='w',
                 edge_width=1., connect='strip'):
        if line_kind != '-':
            raise ValueError('Only solid lines currently supported')
        self._line = LineVisual(method='gl', antialias=False)
        self._markers = MarkersVisual()
        self._kwargs = {}
        CompoundVisual.__init__(self, [self._line, self._markers])
        self.set_data(data, color=color, symbol=symbol,
                      width=width, marker_size=marker_size,
                      edge_color=edge_color, face_color=face_color,
                      edge_width=edge_width, connect=connect)

    def set_data(self, data=None, **kwargs):
        """Set the line data

        Parameters
        ----------
        data : array-like
            The data.
        **kwargs : dict
            Keywoard arguments to pass to MarkerVisual and LineVisal.
        """
        bad_keys = set(kwargs) - self._valid_kwargs
        if bad_keys:
            raise TypeError("Invalid keyword arguments: {}".format(", ".join(bad_keys)))

        # remember these kwargs for future updates
        self._kwargs.update(kwargs)
        if data is None:
            pos = None
        else:
            if isinstance(data, tuple):
                pos = np.array(data).T.astype(np.float32)
            else:
                pos = np.atleast_1d(data).astype(np.float32)

            if pos.ndim == 1:
                pos = pos[:, np.newaxis]
            elif pos.ndim > 2:
                raise ValueError('data must have at most two dimensions')

            if pos.size == 0:
                pos = self._line.pos

                # if both args and keywords are zero, then there is no
                # point in calling this function.
                if len(self._kwargs) == 0:
                    raise TypeError("neither line points nor line properties"
                                    "are provided")
            elif pos.shape[1] == 1:
                x = np.arange(pos.shape[0], dtype=np.float32)[:, np.newaxis]
                pos = np.concatenate((x, pos), axis=1)
            # if args are empty, don't modify position
            elif pos.shape[1] > 3:
                raise TypeError("Too many coordinates given (%s; max is 3)."
                                % pos.shape[1])

        # todo: have both sub-visuals share the same buffers.
        line_kwargs = {}
        for k in self._line_kwargs:
            if k in self._kwargs:
                k_ = self._kw_trans[k] if k in self._kw_trans else k
                line_kwargs[k] = self._kwargs.get(k_)
        if pos is not None or len(line_kwargs) > 0:
            self._line.set_data(pos=pos, **line_kwargs)

        marker_kwargs = {}
        for k in self._marker_kwargs:
            if k in self._kwargs:
                k_ = self._kw_trans[k] if k in self._kw_trans else k
                marker_kwargs[k_] = self._kwargs.get(k)
        if pos is not None or len(marker_kwargs) > 0:
            self._markers.set_data(pos=pos, **marker_kwargs)
