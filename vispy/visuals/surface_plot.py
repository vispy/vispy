# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .mesh import MeshVisual
from ..geometry import MeshData


class SurfacePlotVisual(MeshVisual):
    """Displays a surface plot on a regular x,y grid

    Parameters
    ----------
    x : ndarray | None
        1D array of values specifying the x positions of vertices in the
        grid. If None, values will be assumed to be integers.
    y : ndarray | None
        1D array of values specifying the x positions of vertices in the
        grid. If None, values will be assumed to be integers.
    z : ndarray
        2D array of height values for each grid vertex.
    colors : ndarray
        (width, height, 4) array of vertex colors.

    Notes
    -----
    All arguments are optional.

    Note that if vertex positions are updated, the normal vectors for each
    triangle must be recomputed. This is somewhat expensive if the surface
    was initialized with smooth=False and very expensive if smooth=True.
    For faster performance, initialize with compute_normals=False and use
    per-vertex colors or a material that does not require normals.
    """
    def __init__(self, x=None, y=None, z=None, colors=None, **kwargs):
        # The x, y, z, and colors arguments are passed to set_data().
        # All other keyword arguments are passed to MeshVisual.__init__().
        self._x = None
        self._y = None
        self._z = None
        self.__vertices = None
        self.__faces = None
        self.__meshdata = MeshData()
        kwargs.setdefault('shading', 'smooth')
        MeshVisual.__init__(self, **kwargs)
        self.set_data(x, y, z, colors)

    def set_data(self, x=None, y=None, z=None, colors=None):
        """Update the data in this surface plot.

        Parameters
        ----------
        x : ndarray | None
            1D array of values specifying the x positions of vertices in the
            grid. If None, values will be assumed to be integers.
        y : ndarray | None
            1D array of values specifying the x positions of vertices in the
            grid. If None, values will be assumed to be integers.
        z : ndarray
            2D array of height values for each grid vertex.
        colors : ndarray
            (width, height, 4) array of vertex colors.
        """
        if x is not None:
            if self._x is None or len(x) != len(self._x):
                self.__vertices = None
            self._x = x

        if y is not None:
            if self._y is None or len(y) != len(self._y):
                self.__vertices = None
            self._y = y

        if z is not None:
            if self._x is not None and z.shape[0] != len(self._x):
                raise TypeError('Z values must have shape (len(x), len(y))')
            if self._y is not None and z.shape[1] != len(self._y):
                raise TypeError('Z values must have shape (len(x), len(y))')
            self._z = z
            if (self.__vertices is not None and
                    self._z.shape != self.__vertices.shape[:2]):
                self.__vertices = None

        if self._z is None:
            return

        update_mesh = False
        new_vertices = False

        # Generate vertex and face array
        if self.__vertices is None:
            new_vertices = True
            self.__vertices = np.empty((self._z.shape[0], self._z.shape[1], 3),
                                       dtype=np.float32)
            self.generate_faces()
            self.__meshdata.set_faces(self.__faces)
            update_mesh = True

        # Copy x, y, z data into vertex array
        if new_vertices or x is not None:
            if x is None:
                if self._x is None:
                    x = np.arange(self._z.shape[0])
                else:
                    x = self._x
            self.__vertices[:, :, 0] = x.reshape(len(x), 1)
            update_mesh = True

        if new_vertices or y is not None:
            if y is None:
                if self._y is None:
                    y = np.arange(self._z.shape[1])
                else:
                    y = self._y
            self.__vertices[:, :, 1] = y.reshape(1, len(y))
            update_mesh = True

        if new_vertices or z is not None:
            self.__vertices[..., 2] = self._z
            update_mesh = True

        if colors is not None:
            self.__meshdata.set_vertex_colors(colors)
            update_mesh = True

        # Update MeshData
        if update_mesh:
            self.__meshdata.set_vertices(
                self.__vertices.reshape(self.__vertices.shape[0] *
                                        self.__vertices.shape[1], 3))
            MeshVisual.set_data(self, meshdata=self.__meshdata)

    def generate_faces(self):
        cols = self._z.shape[1]-1
        rows = self._z.shape[0]-1
        faces = np.empty((cols*rows*2, 3), dtype=np.uint)
        rowtemplate1 = (np.arange(cols).reshape(cols, 1) +
                        np.array([[0, 1, cols+1]]))
        rowtemplate2 = (np.arange(cols).reshape(cols, 1) +
                        np.array([[cols+1, 1, cols+2]]))
        for row in range(rows):
            start = row * cols * 2
            faces[start:start+cols] = rowtemplate1 + row * (cols+1)
            faces[start+cols:start+(cols*2)] = rowtemplate2 + row * (cols+1)
        self.__faces = faces
