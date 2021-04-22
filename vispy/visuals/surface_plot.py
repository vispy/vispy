# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
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
        1D/2D array of values specifying the x positions of vertices in the
        grid. In case 1D array given as input, the values will be replicated
        to fill the 2D array of size(z). If None, values will be assumed to
        be integers.
    y : ndarray | None
        1D/2D array of values specifying the y positions of vertices in the
        grid. In case 1D array given as input, the values will be replicated
        to fill the 2D array of size(z). If None, values will be assumed to
        be integers.
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

    def _update_x_data(self, x):
        if x is not None:
            if self._x is None or len(x) != len(self._x):
                self.__vertices = None
            self._x = x

    def _update_y_data(self, y):
        if y is not None:
            if self._y is None or len(y) != len(self._y):
                self.__vertices = None
            self._y = y

    def _update_z_data(self, z):
        if z is not None:
            if self._x is not None and z.shape[0] != len(self._x):
                raise TypeError('Z values must have shape (len(x), len(y))')
            if self._y is not None and z.shape[1] != len(self._y):
                raise TypeError('Z values must have shape (len(x), len(y))')
            self._z = z
            if (self.__vertices is not None and
                    self._z.shape != self.__vertices.shape[:2]):
                self.__vertices = None

    def _update_mesh_vertices(self, x_is_new, y_is_new, z_is_new):
        new_vertices = False
        update_vertices = False
        update_faces = False

        # Generate vertex and face array
        if self.__vertices is None:
            self.__vertices = np.empty((self._z.shape[0], self._z.shape[1], 3),
                                       dtype=np.float32)
            self.__faces = self._generate_faces()
            new_vertices = True
            update_faces = True

        # Copy x, y, z data into vertex array
        if new_vertices or x_is_new:
            if not x_is_new and self._x is None:
                x = np.arange(self._z.shape[0])
            else:
                x = self._x
            if x.ndim == 1:
                x = x.reshape(len(x), 1)
            # Copy the 2D data into the appropriate slice
            self.__vertices[:, :, 0] = x
            update_vertices = True

        if new_vertices or y_is_new:
            if not y_is_new and self._y is None:
                y = np.arange(self._z.shape[1])
            else:
                y = self._y
            if y.ndim == 1:
                y = y.reshape(1, len(y))
            # Copy the 2D data into the appropriate slice
            self.__vertices[:, :, 1] = y
            update_vertices = True

        if new_vertices or z_is_new:
            self.__vertices[..., 2] = self._z
            update_vertices = True
        return update_faces, update_vertices

    def _prepare_mesh_colors(self, colors):
        if colors is None:
            return
        colors = np.asarray(colors)
        if colors.ndim == 3:
            # convert (width, height, 4) to (num_verts, 4)
            vert_shape = self.__vertices.shape
            num_vertices = vert_shape[0] * vert_shape[1]
            colors = colors.reshape(num_vertices, 3)
        return colors

    def set_data(self, x=None, y=None, z=None, colors=None):
        """Update the data in this surface plot.

        Parameters
        ----------
        x : ndarray | None
            1D/2D array of values specifying the x positions of vertices in
            the grid. In case 1D array given as input, the values will be
            replicated to fill the 2D array of size(z). If None, values will be
            assumed to be integers.
        y : ndarray | None
            1D/2D array of values specifying the x positions of vertices in
            the grid. In case 1D array given as input, the values will be
            replicated to fill the 2D array of size(z). If None, values will be
            assumed to be integers.
        z : ndarray
            2D array of height values for each grid vertex.
        colors : ndarray
            (width, height, 4) array of vertex colors.
        """
        self._update_x_data(x)
        self._update_y_data(y)
        self._update_z_data(z)

        if self._z is None:
            # no mesh data to plot so no need to update
            return

        update_faces, update_vertices = self._update_mesh_vertices(
            x is not None,
            y is not None,
            z is not None
        )

        colors = self._prepare_mesh_colors(colors)
        update_colors = colors is not None
        if update_colors:
            self.__meshdata.set_vertex_colors(colors)
        if update_faces:
            self.__meshdata.set_faces(self.__faces)
        if update_vertices:
            self.__meshdata.set_vertices(
                self.__vertices.reshape(self.__vertices.shape[0] *
                                        self.__vertices.shape[1], 3))
        if update_faces or update_vertices or update_colors:
            MeshVisual.set_data(self, meshdata=self.__meshdata)

    def _generate_faces(self):
        cols = self._z.shape[1] - 1
        rows = self._z.shape[0] - 1
        faces = np.empty((cols * rows * 2, 3), dtype=np.uint)
        rowtemplate1 = (np.arange(cols).reshape(cols, 1) +
                        np.array([[0, 1, cols + 1]]))
        rowtemplate2 = (np.arange(cols).reshape(cols, 1) +
                        np.array([[cols + 1, 1, cols + 2]]))
        for row in range(rows):
            start = row * cols * 2
            faces[start:start + cols] = rowtemplate1 + row * (cols + 1)
            faces[start + cols:start + (cols * 2)] =\
                rowtemplate2 + row * (cols + 1)
        return faces
