# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from .mesh import MeshVisual
from ..geometry.isosurface import isosurface
from ..color import Color


class IsosurfaceVisual(MeshVisual):
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
    def __init__(self, data=None, level=None, vertex_colors=None,
                 face_colors=None, color=(0.5, 0.5, 1, 1), **kwargs):
        self._data = None
        self._level = level
        self._vertex_colors = vertex_colors
        self._face_colors = face_colors
        self._color = Color(color)
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

    def set_data(self, data=None, vertex_colors=None, face_colors=None,
                 color=None):
        """ Set the scalar array data

        Parameters
        ----------
        data : ndarray
            A 3D array of scalar values. The isosurface is constructed to show
            all locations in the scalar field equal to ``self.level``.
        vertex_colors : array-like | None
            Colors to use for each vertex.
        face_colors : array-like | None
            Colors to use for each face.
        color : instance of Color
            The color to use.
        """
        # We only change the internal variables if they are provided
        if data is not None:
            self._data = data
        if vertex_colors is not None:
            self._vertex_colors = vertex_colors
        if face_colors is not None:
            self._face_colors = face_colors
        if color is not None:
            self._color = Color(color)
        self._recompute = True
        self.update()

    def _prepare_draw(self, view):
        if self._data is None or self._level is None:
            return False

        if self._recompute:
            verts, faces = isosurface(self._data, self._level)
            MeshVisual.set_data(self, vertices=verts, faces=faces,
                                color=self._color)
            self._recompute = False

        return MeshVisual._prepare_draw(self, view)
