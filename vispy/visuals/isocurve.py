# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .line import LineVisual
from ..color import ColorArray
from ..color.colormap import _normalize, get_colormap
from ..geometry.isocurve import isocurve
from ..testing import has_matplotlib

# checking for matplotlib
_HAS_MPL = has_matplotlib()
if _HAS_MPL:
    from matplotlib import _cntr as cntr


class IsocurveVisual(LineVisual):
    """Displays an isocurve of a 2D scalar array.

    Parameters
    ----------
    data : ndarray | None
        2D scalar array.
    levels : ndarray, shape (Nlev,) | None
        The levels at which the isocurve is constructed from "*data*".
    color_lev : Color, colormap name, tuple, list or array
        The color to use when drawing the line. If a list is given, it
        must be of shape (Nlev), if an array is given, it must be of
        shape (Nlev, ...). and provide one color per level (rgba, colorname).
    clim : tuple
        (min, max) limits to apply when mapping level values through a
        colormap.
    **kwargs : dict
        Keyword arguments to pass to `LineVisual`.

    Notes
    -----
    """
    def __init__(self, data=None, levels=None, color_lev=None, clim=None,
                 **kwargs):
        self._data = None
        self._levels = levels
        self._color_lev = color_lev
        self._clim = clim
        self._need_color_update = True
        self._need_level_update = True
        self._need_recompute = True
        self._X = None
        self._Y = None
        self._iso = None
        self._level_min = None
        self._data_is_uniform = False
        self._lc = None
        self._cl = None
        self._li = None
        self._connect = None
        self._verts = None
        kwargs['method'] = 'gl'
        kwargs['antialias'] = False
        LineVisual.__init__(self, **kwargs)
        if data is not None:
            self.set_data(data)

    @property
    def levels(self):
        """ The threshold at which the isocurve is constructed from the
        2D data.
        """
        return self._levels

    @levels.setter
    def levels(self, levels):
        self._levels = levels
        self._need_level_update = True
        self._need_recompute = True
        self.update()

    @property
    def color(self):
        return self._color_lev

    @color.setter
    def color(self, color):
        self._color_lev = color
        self._need_level_update = True
        self._need_color_update = True
        self.update()

    def set_data(self, data):
        """ Set the scalar array data

        Parameters
        ----------
        data : ndarray
            A 2D array of scalar values. The isocurve is constructed to show
            all locations in the scalar field equal to ``self.levels``.
        """
        self._data = data

        # if using matplotlib isoline algorithm we have to check for meshgrid
        # and we can setup the tracer object here
        if _HAS_MPL:
            if self._X is None or self._X.T.shape != data.shape:
                self._X, self._Y = np.meshgrid(np.arange(data.shape[0]),
                                               np.arange(data.shape[1]))
            self._iso = cntr.Cntr(self._X, self._Y, self._data.astype(float))

        if self._clim is None:
            self._clim = (data.min(), data.max())

        # sanity check,
        # should we raise an error here, since no isolines can be drawn?
        # for now, _prepare_draw returns False if no isoline can be drawn
        if self._data.min() != self._data.max():
            self._data_is_uniform = False
        else:
            self._data_is_uniform = True

        self._need_recompute = True
        self.update()

    def _get_verts_and_connect(self, paths):
        """ retrieve vertices and connects from given paths-list
        """
        verts = np.vstack(paths)
        gaps = np.add.accumulate(np.array([len(x) for x in paths])) - 1
        connect = np.ones(gaps[-1], dtype=bool)
        connect[gaps[:-1]] = False
        return verts, connect

    def _compute_iso_line(self):
        """ compute LineVisual vertices, connects and color-index
        """
        level_index = []
        connects = []
        verts = []

        # calculate which level are within data range
        # this works for now and the existing examples, but should be tested
        # thoroughly also with the data-sanity check in set_data-function
        choice = np.nonzero((self.levels > self._data.min()) &
                            (self._levels < self._data.max()))
        levels_to_calc = np.array(self.levels)[choice]

        # save minimum level index
        self._level_min = choice[0][0]

        for level in levels_to_calc:
            # if we use matplotlib isoline algorithm we need to add half a
            # pixel in both (x,y) dimensions because isolines are aligned to
            # pixel centers
            if _HAS_MPL:
                nlist = self._iso.trace(level, level, 0)
                paths = nlist[:len(nlist)//2]
                v, c = self._get_verts_and_connect(paths)
                v += np.array([0.5, 0.5])
            else:
                paths = isocurve(self._data.astype(float).T, level,
                                 extend_to_edge=True, connected=True)
                v, c = self._get_verts_and_connect(paths)

            level_index.append(v.shape[0])
            connects.append(np.hstack((c, [False])))
            verts.append(v)

        self._li = np.hstack(level_index)
        self._connect = np.hstack(connects)
        self._verts = np.vstack(verts)

    def _compute_iso_color(self):
        """ compute LineVisual color from level index and corresponding color
        """
        level_color = []
        colors = self._lc
        for i, index in enumerate(self._li):
            level_color.append(np.zeros((index, 4)) +
                               colors[i+self._level_min])
        self._cl = np.vstack(level_color)

    def _levels_to_colors(self):
        # computes ColorArrays for given levels
        # try _color_lev as colormap, except as everything else
        try:
            f_color_levs = get_colormap(self._color_lev)
        except:
            colors = ColorArray(self._color_lev).rgba
        else:
            lev = _normalize(self._levels, self._clim[0], self._clim[1])
            # map function expects (Nlev,1)!
            colors = f_color_levs.map(lev[:, np.newaxis])

        # broadcast to (nlev, 4) array
        if len(colors) == 1:
            colors = colors * np.ones((len(self._levels), 1))

        # detect color_lev/levels mismatch and raise error
        if (len(colors) != len(self._levels)):
            raise TypeError("Color/level mismatch. Color must be of shape "
                            "(Nlev, ...) and provide one color per level")

        self._lc = colors

    def _prepare_draw(self, view):
        if (self._data is None or self._levels is None or
                self._color_lev is None or self._data_is_uniform):
            return False

        if self._need_level_update:
            self._levels_to_colors()
            self._need_level_update = False

        if self._need_recompute:
            self._compute_iso_line()
            self._compute_iso_color()
            LineVisual.set_data(self, pos=self._verts, connect=self._connect,
                                color=self._cl)
            self._need_recompute = False

        if self._need_color_update:
            self._compute_iso_color()
            LineVisual.set_data(self, color=self._cl)
            self._need_color_update = False

        return LineVisual._prepare_draw(self, view)
