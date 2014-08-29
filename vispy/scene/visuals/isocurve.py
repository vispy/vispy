# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .line import Line
from ...geometry.isocurve import isocurve


class Isocurve(Line):
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
    def __init__(self, data=None, level=None, **kwds):
        self._data = None
        self._level = level
        self._recompute = True
        kwds['mode'] = 'gl'
        kwds['antialias'] = False
        Line.__init__(self, **kwds)
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

        Parameters:
        -----------
        data : ndarray
            A 2D array of scalar values. The isocurve is constructed to show
            all locations in the scalar field equal to ``self.level``.
        """
        self._data = data
        self._recompute = True
        self.update()

    def draw(self, event):
        if self._data is None or self._level is None:
            return
        
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
            Line.set_data(self, pos=verts, connect=connect)
            self._recompute = False
            
        Line.draw(self, event)
