# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .line import LineVisual
from ..color import ColorArray, get_colormap_py
from ..ext.six import string_types


def normalize(mag, cmin, cmax):
    """ mag is a scalar or an array with Nmag element Return an array (Nmag)
    element of floats between 0 and 1 """
    mag = np.array(mag)
    try:
        shape = mag.shape[0]
    except:
        shape = 1
    if cmin != cmax:
        return (mag-cmin)/float(cmax-cmin)
    else:
        return np.zeros(shape) + 0.5


def iso_mesh_line(vertices, tris, vertex_data, level):
    """
    Generate isocurve from vertex data in a surface mesh with triangular
    element using marching squares algorithm.

    Parameters
    ----------
    vertices : ndarray, shape (Nv, 3)
        Vertex coordinates.
    tris : ndarray, shape (Nf, 3)
        Indices of triangular element into the vertex array.
    vertex_data : ndarray, shape (Nv)
        data at vertex.
    level : ndarray, shape (Nl)
        Levels at which to generate an isocurve
    tol : float
        tolerance for merge vertex

    Return
    ------
    a np array of vertices (Nvout, 3)
    a np array for line connect (Ne, 2)
    and a np array for vertices line index (Nvout)
    """

    lines = None
    connects = None
    vertex_level = None
    if (isinstance(vertices, np.ndarray) and isinstance(tris, np.ndarray)
       and isinstance(vertex_data, np.ndarray)
       and isinstance(level, np.ndarray)):
        if vertices.shape[1] <= 3:
            verts = vertices
        elif vertices.shape[1] == 4:
            verts = vertices[:, :-1]
        else:
            verts = None

        if (verts is not None and tris.shape[1] == 3
           and vertex_data.shape[0] == verts.shape[0]):
            edges = np.vstack((tris.reshape((-1)),
                               np.roll(tris, -1, axis=1).reshape((-1)))).T
            edge_datas = vertex_data[edges]
            edge_coors = verts[edges].reshape(tris.shape[0]*3, 2, 3)
            for lev in level:
                # index for select edges with vertices have only False - True
                # or True - False at extremity
                index = (edge_datas >= lev)
                index = index[:, 0] ^ index[:, 1]  # xor calculation
                # Selectect edge
                edge_datas_Ok = edge_datas[index, :]
                xyz = edge_coors[index]
                # Linear interpolation
                ratio = np.array([(lev - edge_datas_Ok[:, 0]) /
                                  (edge_datas_Ok[:, 1] - edge_datas_Ok[:, 0])])
                point = xyz[:, 0, :] + ratio.T*(xyz[:, 1, :] - xyz[:, 0, :])
                nbr = point.shape[0]//2
                if connects is not None:
                    connect = np.arange(0, nbr*2).reshape((nbr, 2)) + \
                        len(lines)
                    connects = np.append(connects, connect, axis=0)
                    lines = np.append(lines, point, axis=0)
                    vertex_level = np.append(vertex_level,
                                             np.zeros(len(point)) +
                                             lev)
                else:
                    lines = point
                    connects = np.arange(0, nbr*2).reshape((nbr, 2)) + \
                        len(lines)
                    vertex_level = np.zeros(len(point)) + lev

    return lines, connects, vertex_level


class IsolineVisual(LineVisual):
    """Displays the isocurves of a tri mesh with data at vertices at different
    levels.

    Parameters
    ----------
    vertices : ndarray, shape (Nv, 3) | None
        Vertex coordinates.
    tris : ndarray, shape (Nf, 3) | None
        Indices into the vertex array.
    data : ndarray, shape (Nv) | None
        scalar at vertices
    level: ndarrat, shape (Nlev) | None
        The levels at which the isocurve is constructed from *data*.
    color : Color, tuple, colormap name or array
        The color to use when drawing the line. If an array is given, it
        must be of shape (Nlev, 4) and provide one rgba color by level.
    Notes
    -----
    """
    def __init__(self, vertices=None, tris=None, data=None,
                 level=None, color_lev=None, **kwds):
        self._data = None
        self._vertices = None
        self._tris = None
        self._level = level
        self._color_lev = color_lev
        self._update_color_lev = True
        self._recompute = True
        kwds['antialias'] = False
        LineVisual.__init__(self, mode='gl', **kwds)
        self.set_data(vertices=vertices, tris=tris, data=data)

    @property
    def get_level(self):
        """ The threshold at which the isocurves are constructed from the data.
        """
        return self._level

    def set_level(self, level):
        self._level = level
        self._recompute = True
        self.update()

    @property
    def get_data(self):
        """The mesh data"""
        return self._vertices, self._tris, self._data

    def set_data(self, vertices=None, tris=None, data=None):
        # modifier pour tenier compte des None self._recompute = True
        if data is not None:
            self._data = data
            self._recompute = True
        if vertices is not None:
            self._vertices = vertices
            self._recompute = True
        if tris is not None:
            self._tris = tris
            self._recompute = True
        self.update()

    @property
    def get_color(self):
        return self._color_lev

    def set_color(self, color):
        if color is not None:
            self._color_lev = color
            self._update_color_lev = True
            self.update()

    def _level_to_colors(self):
        if isinstance(self._color_lev, string_types):
            f_color_levs = get_colormap_py(self._color_lev)
            lev = normalize(self._vl, self._vl.min(), self._vl.max())
            colors = np.array([f_color_levs(x) for x in lev])
        else:
            colors = ColorArray(self._color_lev).rgba
            if len(colors) == 1:
                colors = colors[0]
        return colors

    def draw(self, transforms):
        if (self._data is None or self._level is None or self._tris is None or
           self._vertices is None or self._color_lev is None):
            return

        if self._recompute:
            self._v, self._c, self._vl = iso_mesh_line(self._vertices,
                                                       self._tris, self._data,
                                                       self._level)
            self._cl = self._level_to_colors()
            self._recompute = False
            self._update_color_lev = False

        if self._update_color_lev:
            self._cl = self._level_to_colors()
            self._update_color_lev = False

        LineVisual.set_data(self, pos=self._v, connect=self._c, color=self._cl)
        LineVisual.draw(self, transforms)
