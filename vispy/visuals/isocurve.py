# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .line import LineVisual
from ..geometry.isocurve import isocurve


class IsocurveVisual(LineVisual):
    """Displays an isocurve of a 2D scalar array.

    Parameters
    ----------
    data : ndarray | None
        2D scalar array.
    level: float | None
        The level at which the isocurve is constructed from *data*.

    Notes
    -----
    """
    def __init__(self, data=None, level=None, **kwargs):
        self._data = None
        self._level = level
        self._recompute = True
        kwargs['method'] = 'gl'
        kwargs['antialias'] = False
        LineVisual.__init__(self, **kwargs)
        if data is not None:
            self.set_data(data)

    @property
    def level(self):
        """ The threshold at which the isocurve is constructed from the
        2D data.
        """
        return self._level

    @level.setter
    def level(self, level):
        self._level = level
        self._recompute = True
        self.update()

    def set_data(self, data):
        """ Set the scalar array data

        Parameters
        ----------
        data : ndarray
            A 2D array of scalar values. The isocurve is constructed to show
            all locations in the scalar field equal to ``self.level``.
        """
        self._data = data
        self._recompute = True
        self.update()

    def _prepare_draw(self, view):
        if self._data is None or self._level is None:
            return False

        if self._recompute:
            verts = []
            paths = isocurve(self._data.astype(float).T, self._level,
                             extend_to_edge=True, connected=True)
            tot = 0
            gaps = []
            for path in paths:
                verts.extend(path)
                tot += len(path)
                gaps.append(tot-1)

            connect = np.ones(tot-1, dtype=bool)
            connect[gaps[:-1]] = False

            verts = np.array(verts)
            LineVisual.set_data(self, pos=verts, connect=connect)
            self._recompute = False
        
        return LineVisual._prepare_draw(self, view)
