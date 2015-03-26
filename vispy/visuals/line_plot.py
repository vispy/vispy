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
    args : array | two arrays
        Arguments can be passed as (Y,), (X, Y) or (np.array((X, Y))).
    kwargs : keyword arguments
        Keyword arguments to pass on to the LineVisual and Marker visuals.
        Supported arguments are width, connect, color, edge_color, face_color,
        and edge_width.

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
    _line_kwargs = ['width', 'connect', 'color']
    _marker_kwargs = ['edge_color', 'face_color', 'edge_width']

    def __init__(self, *args, **kwargs):
        my_kwargs = {}
        for k in self._line_kwargs + self._marker_kwargs:
            if k in kwargs:
                my_kwargs[k] = kwargs.pop(k)

        Visual.__init__(self, **kwargs)
        self._line = LineVisual()
        self._markers = MarkersVisual()

        self.set_data(*args, **my_kwargs)

    def set_data(self, *args, **kwargs):
        args = [np.array(x) for x in args]

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
                line_kwargs[k] = kwargs.pop(k)
        self._line.set_data(pos=pos, **line_kwargs)
        marker_kwargs = {}
        for k in self._marker_kwargs:
            if k in kwargs:
                marker_kwargs[k] = kwargs.pop(k)
        self._markers.set_data(pos=pos, **marker_kwargs)
        if len(kwargs) > 0:
            raise TypeError("Invalid keyword arguments: %s" % kwargs.keys())

    def bounds(self, mode, axis):
        return self._line.bounds(mode, axis)

    def draw(self, transforms):
        for v in self._line, self._markers:
            v.draw(transforms)
