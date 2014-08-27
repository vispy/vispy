# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from .mesh import Mesh
from ...geometry.isosurface import isosurface


class Isosurface(Mesh):
    """Displays an isosurface of a 3D scalar array.

    Parameters
    ----------
    data : ndarray | None
        3D scalar array.
    level: float | None
        The level at which the isosurface is constructed from *data*.

    Notes
    -----
    """
    def __init__(self, data=None, level=None, **kwds):
        self._data = None
        self._level = level
        self._recompute = True
        Mesh.__init__(self, **kwds)
        if data is not None:
            self.set_data(data)

    @property
    def level(self):
        """ The threshold at which the isosurface is constructed from the 
        3D data.
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
            A 3D array of scalar values. The isosurface is constructed to show
            all locations in the scalar field equal to ``self.level``.
        """
        self._data = data
        self._recompute = True
        self.update()

    def draw(self, event):
        if self._data is None or self._level is None:
            return
        
        if self._recompute:
            verts, faces = isosurface(self._data, self._level)
            Mesh.set_data(self, vertices=verts, faces=faces)
            self._recompute = False
            
        Mesh.draw(self, event)
