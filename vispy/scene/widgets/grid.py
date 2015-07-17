# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import warnings
import numpy as np

from .widget import Widget
from ...util.np_backport import nanmean


class Grid(Widget):
    """
    Widget that automatically sets the position and size of child Widgets to
    proportionally divide its internal area into a grid.

    Parameters
    ----------
    spacing : int
        Spacing between widgets.
    **kwargs : dict
        Keyword arguments to pass to `Widget`.
    """
    def __init__(self, spacing=6, **kwargs):
        from .viewbox import ViewBox
        self._next_cell = [0, 0]  # row, col
        self._cells = {}
        self._grid_widgets = {}
        self.spacing = spacing
        self._n_added = 0
        self._default_class = ViewBox  # what to add when __getitem__ is used
        Widget.__init__(self, **kwargs)

    def __getitem__(self, idxs):
        """Return an item or create it if the location is available"""
        if not isinstance(idxs, tuple):
            idxs = (idxs,)
        if len(idxs) == 1:
            idxs = idxs + (slice(None),)
        elif len(idxs) != 2:
            raise ValueError('Incorrect index: %s' % (idxs,))
        lims = np.empty((2, 2), int)
        for ii, idx in enumerate(idxs):
            if isinstance(idx, int):
                idx = slice(idx, idx + 1, None)
            if not isinstance(idx, slice):
                raise ValueError('indices must be slices or integers, not %s'
                                 % (type(idx),))
            if idx.step is not None and idx.step != 1:
                raise ValueError('step must be one or None, not %s' % idx.step)
            start = 0 if idx.start is None else idx.start
            end = self.grid_size[ii] if idx.stop is None else idx.stop
            lims[ii] = [start, end]
        layout = self.layout_array
        existing = layout[lims[0, 0]:lims[0, 1], lims[1, 0]:lims[1, 1]] + 1
        if existing.any():
            existing = set(list(existing.ravel()))
            ii = list(existing)[0] - 1
            if len(existing) != 1 or ((layout == ii).sum() !=
                                      np.prod(np.diff(lims))):
                raise ValueError('Cannot add widget (collision)')
            return self._grid_widgets[ii][-1]
        spans = np.diff(lims)[:, 0]
        item = self.add_widget(self._default_class(),
                               row=lims[0, 0], col=lims[1, 0],
                               row_span=spans[0], col_span=spans[1])
        return item

    def add_widget(self, widget=None, row=None, col=None, row_span=1,
                   col_span=1):
        """
        Add a new widget to this grid. This will cause other widgets in the
        grid to be resized to make room for the new widget.

        Parameters
        ----------
        widget : Widget
            The Widget to add
        row : int
            The row in which to add the widget (0 is the topmost row)
        col : int
            The column in which to add the widget (0 is the leftmost column)
        row_span : int
            The number of rows to be occupied by this widget. Default is 1.
        col_span : int
            The number of columns to be occupied by this widget. Default is 1.

        Notes
        -----
        The widget's parent is automatically set to this grid, and all other
        parent(s) are removed.
        """
        if row is None:
            row = self._next_cell[0]
        if col is None:
            col = self._next_cell[1]

        if widget is None:
            widget = Widget()

        _row = self._cells.setdefault(row, {})
        _row[col] = widget
        self._grid_widgets[self._n_added] = (row, col, row_span, col_span,
                                             widget)
        self._n_added += 1
        widget.parent = self

        self._next_cell = [row, col+col_span]

        # update stretch based on colspan/rowspan
        stretch = list(widget.stretch)
        stretch[0] = col_span if stretch[0] is None else stretch[0]
        stretch[1] = row_span if stretch[1] is None else stretch[1]
        widget.stretch = stretch

        self._update_child_widgets()
        return widget

    def add_grid(self, row=None, col=None, row_span=1, col_span=1,
                 **kwargs):
        """
        Create a new Grid and add it as a child widget.

        Parameters
        ----------
        row : int
            The row in which to add the widget (0 is the topmost row)
        col : int
            The column in which to add the widget (0 is the leftmost column)
        row_span : int
            The number of rows to be occupied by this widget. Default is 1.
        col_span : int
            The number of columns to be occupied by this widget. Default is 1.
        **kwargs : dict
            Keyword arguments to pass to the new `Grid`.
        """
        from .grid import Grid
        grid = Grid(**kwargs)
        return self.add_widget(grid, row, col, row_span, col_span)

    def add_view(self, row=None, col=None, row_span=1, col_span=1,
                 **kwargs):
        """
        Create a new ViewBox and add it as a child widget.

        Parameters
        ----------
        row : int
            The row in which to add the widget (0 is the topmost row)
        col : int
            The column in which to add the widget (0 is the leftmost column)
        row_span : int
            The number of rows to be occupied by this widget. Default is 1.
        col_span : int
            The number of columns to be occupied by this widget. Default is 1.
        **kwargs : dict
            Keyword arguments to pass to `ViewBox`.
        """
        from .viewbox import ViewBox
        view = ViewBox(**kwargs)
        return self.add_widget(view, row, col, row_span, col_span)

    def next_row(self):
        self._next_cell = [self._next_cell[0] + 1, 0]

    @property
    def grid_size(self):
        rvals = [widget[0]+widget[2] for widget in self._grid_widgets.values()]
        cvals = [widget[1]+widget[3] for widget in self._grid_widgets.values()]
        return max(rvals + [0]), max(cvals + [0])

    @property
    def layout_array(self):
        locs = -1 * np.ones(self.grid_size, int)
        for key in self._grid_widgets.keys():
            r, c, rs, cs = self._grid_widgets[key][:4]
            locs[r:r + rs, c:c + cs] = key
        return locs

    def __repr__(self):
        return (('<Grid at %s:\n' % hex(id(self))) +
                str(self.layout_array + 1) + '>')

    def _update_child_widgets(self):
        # Resize all widgets in this grid to share space.
        n_rows, n_cols = self.grid_size
        if n_rows == 0 or n_cols == 0:
            return

        # 1. Collect information about occupied cells and their contents
        occupied = np.zeros((n_rows, n_cols), dtype=bool)
        stretch = np.zeros((n_rows, n_cols, 2), dtype=float)
        stretch[:] = np.nan
        # minsize = np.zeros((n_rows, n_cols, 2), dtype=float)
        for key, val in self._grid_widgets.items():
            w = val[4]
            row, col, rspan, cspan, ch = self._grid_widgets[key]
            occupied[row:row+rspan, col:col+cspan] = True
            stretch[row:row+rspan, col:col+cspan] = (np.array(w.stretch) /
                                                     [cspan, rspan])
        row_occ = occupied.sum(axis=1) > 0
        col_occ = occupied.sum(axis=0) > 0
        with warnings.catch_warnings(record=True):  # mean of empty slice
            row_stretch = nanmean(stretch[..., 1], axis=1)
            col_stretch = nanmean(stretch[..., 0], axis=0)
        row_stretch[np.isnan(row_stretch)] = 0
        col_stretch[np.isnan(col_stretch)] = 0

        # 2. Decide width of each row/col
        rect = self.rect.padded(self.padding + self.margin)
        n_cols = col_occ.sum()
        colspace = rect.width - (n_cols-1) * self.spacing
        colsizes = col_stretch * colspace / col_stretch.sum()
        colsizes[colsizes == 0] = -self.spacing
        n_rows = row_occ.sum()
        rowspace = rect.height - (n_rows-1) * self.spacing
        rowsizes = row_stretch * rowspace / row_stretch.sum()
        rowsizes[rowsizes == 0] = -self.spacing

        # 3. Decide placement of row/col edges
        colend = np.cumsum(colsizes) + self.spacing * np.arange(len(colsizes))
        colstart = colend - colsizes
        rowend = np.cumsum(rowsizes) + self.spacing * np.arange(len(rowsizes))
        rowstart = rowend - rowsizes

        # snap to pixel boundaries to avoid drawing artifacts
        colstart = np.round(colstart) + self.margin
        colend = np.round(colend) + self.margin
        rowstart = np.round(rowstart) + self.margin
        rowend = np.round(rowend) + self.margin

        for key in self._grid_widgets.keys():
            row, col, rspan, cspan, ch = self._grid_widgets[key]

            # Translate the origin of the node to the corner of the area
            # ch.transform.reset()
            # ch.transform.translate((colstart[col], rowstart[row]))
            ch.pos = colstart[col], rowstart[row]

            # ..and set the size to match.
            w = colend[col+cspan-1]-colstart[col]
            h = rowend[row+rspan-1]-rowstart[row]
            ch.size = w, h
