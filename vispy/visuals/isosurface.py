# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from .mesh import MeshVisual
from ..geometry.isosurface import isosurface


class IsosurfaceVisual(MeshVisual):
    """Displays an isosurface of a 3D scalar array.

    Parameters
    ----------
    data : ndarray | None
        3D scalar array.
    level: float | None
        The level at which the isosurface is constructed from *data*.
    **kwargs : dict
        Keyword dict to pass to the MeshVisual constructor.

    Notes
    -----
    """
    def __init__(self, data=None, level=None, **kwargs):
        self._data = None
        self._level = level
        self._recompute = True
        MeshVisual.__init__(self, **kwargs)
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

        Parameters
        ----------
        data : ndarray
            A 3D array of scalar values. The isosurface is constructed to show
            all locations in the scalar field equal to ``self.level``.
        """
        self._data = data
        self._recompute = True
        self.update()

    def _prepare_draw(self, view):
        if self._data is None or self._level is None:
            return False

        if self._recompute:
            verts, faces = isosurface(self._data, self._level)
            MeshVisual.set_data(self, vertices=verts, faces=faces)
            self._recompute = False

        return MeshVisual._prepare_draw(self, view)
