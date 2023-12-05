# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
from typing import Callable

import numpy as np

from .mesh import MeshVisual


class HistogramVisual(MeshVisual):
    """Visual that calculates and displays a histogram of data

    Parameters
    ----------
    data : array-like
        Data to histogram. Currently only 1D data is supported.
    bins : int | array-like
        Number of bins, or bin edges.
    color : instance of Color
        Color of the histogram.
    orientation : {'h', 'v'}
        Orientation of the histogram.
    calc_hist : callable
        Function that computes the histogram. Must accept two positional arguments
        (data, bins) and return (hist_data, bin_edges). Default is numpy.histogram.
    """

    def __init__(
        self,
        hist_data=None,
        bins=10,
        color="w",
        orientation="h",
        calc_hist: Callable = np.histogram,
    ):
        self.orientation = orientation
        if not callable(calc_hist):
            raise TypeError("calc_hist must be a callable that accepts (data, bins).")
        self.calc_hist = calc_hist
        self._bins = bins
        MeshVisual.__init__(self, color=color)
        if hist_data is not None:
            self.set_raw_data(hist_data, bins)

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, orientation: str = "h"):
        if orientation not in ("h", "v"):
            raise ValueError('orientation must be "h" or "v", not %s' % (orientation,))
        self._orientation = orientation

    def set_raw_data(self, data, bins=None, color=None) -> None:
        """Set the data underlying the histogram.
        
        Optionally update bins and color. Provided data will be passed
        to the histogram function (``calc_hist``).
        
        """
        # update bins if provided
        if bins is None:
            bins = self._bins
        else:
            self._bins = bins
        # do the histogramming
        hist_data, bin_edges = self.calc_hist(data, bins)
        # construct our vertices
        verts, faces = self._bins2mesh(hist_data, bin_edges)
        super().set_data(verts, faces, color=color)

    def _bins2mesh(self, hist_data, bin_edges):
        X, Y = (0, 1) if self.orientation == "h" else (1, 0)
        rr = np.zeros((3 * len(bin_edges) - 2, 3), np.float32)
        rr[:, X] = np.repeat(bin_edges, 3)[1:-1]
        rr[1::3, Y] = hist_data
        rr[2::3, Y] = hist_data
        bin_edges.astype(np.float32)
        # and now our tris
        tris = np.zeros((2 * len(bin_edges) - 2, 3), np.uint32)
        offsets = 3 * np.arange(len(bin_edges) - 1, dtype=np.uint32)[:, np.newaxis]
        tri_1 = np.array([0, 2, 1])
        tri_2 = np.array([2, 0, 3])
        tris[::2] = tri_1 + offsets
        tris[1::2] = tri_2 + offsets
        return rr, tris
