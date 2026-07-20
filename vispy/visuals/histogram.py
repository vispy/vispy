# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import numpy as np

from .mesh import MeshVisual

if TYPE_CHECKING:
    from typing import TypeAlias, Literal, SupportsIndex
    import numpy.typing as npt
    from vispy.color.color_array import Color

    BinsLike: TypeAlias = "str | SupportsIndex | npt.ArrayLike"
    HistogramCallable: TypeAlias = Callable[
        [npt.ArrayLike, BinsLike], tuple[npt.NDArray, npt.NDArray]
    ]
    Orientation: TypeAlias = Literal["h", "v"]


class HistogramVisual(MeshVisual):
    """Visual that calculates and displays a histogram of data

    Parameters
    ----------
    data
        Data to histogram.  May be `None` on initialization, use `set_raw_data`
        to set data after initialization.
    bins
        If `bins` is an int, it defines the number of equal-width
        bins in the given range (10, by default). If `bins` is a
        sequence, it defines a monotonically increasing array of bin edges,
        including the rightmost edge, allowing for non-uniform bin widths.
        May also be a string if the calc_hist function supports it.
    color
        Color of the faces in the histogram mesh.
    orientation
        Orientation of the histogram.
    calc_hist
        Function that computes the histogram. Must accept two positional arguments
        (data, bins) and return (hist_data, bin_edges). Default is numpy.histogram.
    **kwargs
        Keyword arguments to pass to `MeshVisual`.
    """

    def __init__(
        self,
        hist_data: npt.ArrayLike | None = None,
        bins: BinsLike = 10,
        color: str | Color = "w",
        orientation: Orientation = "h",
        calc_hist: HistogramCallable = np.histogram,
        **kwargs: Any,
    ):
        self.orientation = orientation
        if not callable(calc_hist):
            raise TypeError("calc_hist must be a callable that accepts (data, bins).")
        self.calc_hist = calc_hist
        self._bins = bins
        MeshVisual.__init__(self, color=color, **kwargs)
        if hist_data is not None:
            self.set_raw_data(hist_data, bins)

    @property
    def orientation(self) -> Orientation:
        return self._orientation

    @orientation.setter
    def orientation(self, orientation: Orientation = "h") -> None:
        if orientation not in ("h", "v"):
            raise ValueError('orientation must be "h" or "v", not %s' % (orientation,))
        self._orientation = orientation

    def set_raw_data(
        self,
        data: npt.ArrayLike,
        bins: BinsLike | None = None,
        color: str | Color | None = None,
    ) -> None:
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
        # construct our vertices and update the mesh
        verts, faces = self._bins2mesh(hist_data, bin_edges)
        super().set_data(verts, faces, color=color)

    def _bins2mesh(self, hist_data: npt.NDArray, bin_edges: npt.NDArray) -> tuple:
        """Convert histogram data and bin edges to vertices and faces."""
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
