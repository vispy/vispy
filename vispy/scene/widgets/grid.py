# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import warnings
import numpy as np

from .widget import Widget
from ...util.np_backport import nanmean

from vispy.ext.cassowary import (SimplexSolver, expression,
                                 Variable, STRONG, MEDIUM, WEAK, REQUIRED)


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

    def _prepare_draw(self, view):
        self._update_child_widgets()
        print("grid update: %s" % self)

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

    # MODIFIED VERSION
    def _update_child_widgets(self):
        # Resize all widgets in this grid to share space.
        n_rows, n_cols = self.grid_size
        if n_rows == 0 or n_cols == 0:
            return
        print("---")

        grid_layout = np.array([[None for _ in range(0, n_cols)]
                                for _ in range(0, n_rows)])

        for key, value in self._grid_widgets.items():
            (row, col, rspan, cspan, widget) = value
            grid_layout[row:row+rspan, col:col+cspan] = widget

        print("grid layout:\n--------\n%s" % grid_layout)

        rect = self.rect.padded(self.padding + self.margin)
        solver = SimplexSolver()

        # x, width constraints ------
        total_w_eqns = [expression.Expression() for _ in range(0, n_cols)]
        total_h_eqns = [expression.Expression() for _ in range(0, n_rows)]

        stretch_w_eqns = []
        stretch_h_eqns = []

        for key, value in self._grid_widgets.items():
            (row, col, rspan, cspan, widget) = value

            widget.var_w = Variable("w-(%s, %s)" % (row, col))
            widget.var_h = Variable("h-(%s, %s)" % (row, col))

            widget.var_x = Variable("x-(%s, %s)" % (row, col))
            widget.var_y = Variable("y-(%s, %s)" % (row, col))

            # position - row
            if row == 0:
                widget.var_y.value = 0
                solver.add_stay(widget.var_y)
            else:
                prev_widget = grid_layout[row - 1][col]
                if prev_widget is not None:
                    solver.add_constraint(widget.var_y == prev_widget.var_y + prev_widget.var_h )

            # position - col
            if col == 0:
                widget.var_x.value = 0
                solver.add_stay(widget.var_x)
            else:
                prev_widget = grid_layout[row][col - 1]
                if prev_widget is not None:
                    solver.add_constraint(widget.var_x == prev_widget.var_x + prev_widget.var_w )

            # dimensions
            for h_eqn in total_h_eqns[col:col+cspan]:
                    h_eqn.add_expression(widget.var_h)

            for w_eqn in total_w_eqns[row:row+rspan]:
                    w_eqn.add_expression(widget.var_w)

            if widget.min_width is not None:
                solver.add_constraint(widget.var_w >= widget.min_width)
            if widget.max_width is not None:
                solver.add_constraint(widget.var_w <= widget.max_width)

            if widget.min_height is not None:
                solver.add_constraint(widget.var_w >= widget.min_height)
            if widget.max_height is not None:
                solver.add_constraint(widget.var_w <= widget.max_height)

            if widget.stretch[0] is not None:
                stretch_w_eqns.append(widget.var_w / widget.stretch[0])

            if widget.stretch[1] is not None:
                stretch_h_eqns.append(widget.var_h / widget.stretch[1])

        print("total w: %s" % (total_w_eqns))
        print("total h: %s" % (total_h_eqns))
        # set total width, height eqns
        for w_eqn in total_w_eqns:
            if len(w_eqn.terms) > 0:
                solver.add_constraint(w_eqn == rect.width, strength=REQUIRED)
        for h_eqn in total_h_eqns:
            if len(h_eqn.terms) > 0:
                solver.add_constraint(h_eqn == rect.height, strength=REQUIRED)

        # add stretch eqns
        if len(stretch_w_eqns) > 1:
            for eqn in stretch_w_eqns[1:]:
                solver.add_constraint(eqn == stretch_w_eqns[0], strength=WEAK)

        if len(stretch_h_eqns) > 1:
            for eqn in stretch_h_eqns[1:]:
                solver.add_constraint(eqn == stretch_h_eqns[0], strength=WEAK)

        solver.solve()

        # copy solution
        for (_, val) in self._grid_widgets.items():
            (row, col, rspan, cspan, widget) = val
            widget.width = widget.var_w.value
            widget.height = widget.var_h.value
            widget.pos = (widget.var_x.value, widget.var_y.value)

            print("----")
            print("row, col: (%s, %s)" % (row, col))
            print("x, y: (%s, %s)" % widget.pos)
            print("w, h: (%s, %s)" % (widget.width, widget.height))
        return

        
    # def _update_child_widgets(self):
    #     # Resize all widgets in this grid to share space.
    #     n_rows, n_cols = self.grid_size
    #     if n_rows == 0 or n_cols == 0:
    #         return

    #     # 1. Collect information about occupied cells and their contents
    #     occupied = np.zeros((n_rows, n_cols), dtype=bool)
    #     stretch = np.zeros((n_rows, n_cols, 2), dtype=float)
    #     stretch[:] = np.nan
    #     #minsize = np.zeros((n_rows, n_cols, 2), dtype=float)
    #     for key, val in self._grid_widgets.items():
    #         w = val[4]
    #         row, col, rspan, cspan, ch = self._grid_widgets[key]
    #         occupied[row:row+rspan, col:col+cspan] = True
    #         stretch[row:row+rspan, col:col+cspan] = (np.array(w.stretch) /
    #                                                  [cspan, rspan])
    #     row_occ = occupied.sum(axis=1) > 0
    #     col_occ = occupied.sum(axis=0) > 0
    #     with warnings.catch_warnings(record=True):  # mean of empty slice
    #         row_stretch = nanmean(stretch[..., 1], axis=1)
    #         col_stretch = nanmean(stretch[..., 0], axis=0)
    #     row_stretch[np.isnan(row_stretch)] = 0
    #     col_stretch[np.isnan(col_stretch)] = 0
        
    #     # 2. Decide width of each row/col
    #     rect = self.rect.padded(self.padding + self.margin)
    #     n_cols = col_occ.sum()
    #     colspace = rect.width - (n_cols-1) * self.spacing
    #     colsizes = col_stretch * colspace / col_stretch.sum()
    #     colsizes[colsizes == 0] = -self.spacing
    #     n_rows = row_occ.sum()
    #     rowspace = rect.height - (n_rows-1) * self.spacing
    #     rowsizes = row_stretch * rowspace / row_stretch.sum()
    #     rowsizes[rowsizes == 0] = -self.spacing
        
    #     # 3. Decide placement of row/col edges
    #     colend = np.cumsum(colsizes) + self.spacing * np.arange(len(colsizes))
    #     colstart = colend - colsizes
    #     rowend = np.cumsum(rowsizes) + self.spacing * np.arange(len(rowsizes))
    #     rowstart = rowend - rowsizes

    #     # snap to pixel boundaries to avoid drawing artifacts
    #     colstart = np.round(colstart) + self.margin
    #     colend = np.round(colend) + self.margin
    #     rowstart = np.round(rowstart) + self.margin
    #     rowend = np.round(rowend) + self.margin

    #     for key in self._grid_widgets.keys():
    #         row, col, rspan, cspan, ch = self._grid_widgets[key]

    #         # Translate the origin of the node to the corner of the area
    #         # ch.transform.reset()
    #         # ch.transform.translate((colstart[col], rowstart[row]))
    #         ch.pos = colstart[col], rowstart[row]

    #         # ..and set the size to match.
    #         w = colend[col+cspan-1]-colstart[col]
    #         h = rowend[row+rspan-1]-rowstart[row]
    #         ch.size = w, h
