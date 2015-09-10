# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division
import numpy as np

from .widget import Widget

from ...ext.cassowary import (SimplexSolver, expression,
                              Variable, STRONG, REQUIRED, WEAK)


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
        self._solver = None
        self._need_solver_recreate = True
        Widget.__init__(self, **kwargs)

        # width and height of the Rect used to place child widgets
        self.var_w = Variable("w_rect")
        self.var_h = Variable("h_rect")
        self.var_x = Variable("x_rect")
        self.var_y = Variable("x_rect")

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

        widget.var_w = Variable("w-(row: %s | col: %s)" % (row, col))
        widget.var_h = Variable("h-(row: %s | col: %s)" % (row, col))

        widget.var_x = Variable("x-(row: %s | col: %s)" % (row, col))
        widget.var_y = Variable("y-(row: %s | col: %s)" % (row, col))

        # update stretch based on colspan/rowspan
        stretch = list(widget.stretch)
        stretch[0] = col_span if stretch[0] is None else stretch[0]
        stretch[1] = row_span if stretch[1] is None else stretch[1]
        widget.stretch = stretch

        self._need_solver_recreate = True

        return widget

    def remove_widget(self, widget):
        """Remove a widget from this grid

        Parameters
        ----------
        widget : Widget
            The Widget to remove
        """

        self._grid_widgets = dict((key, val)
                                  for (key, val) in self._grid_widgets.items()
                                  if val[-1] != widget)

        self._need_solver_recreate = True

    def resize_widget(self, widget, row_span, col_span):
        """Resize a widget in the grid to new dimensions.

        Parameters
        ----------
        widget : Widget
            The widget to resize
        row_span : int
            The number of rows to be occupied by this widget.
        col_span : int
            The number of columns to be occupied by this widget.
        """

        row = None
        col = None

        for (r, c, rspan, cspan, w) in self._grid_widgets.values():
            if w == widget:
                row = r
                col = c

                break

        if row is None or col is None:
            raise ValueError("%s not found in grid" % widget)

        self.remove_widget(widget)
        self.add_widget(widget, row, col, row_span, col_span)
        self._need_solver_recreate = True

    def move_widget(self, widget, row, col):
        """Move the given widget to the specified row and column.

        Parameters
        ----------
        widget : Widget
            The Widget to add
        row : int
            The row in which to move the widget (0 is the topmost row)
        col : int
            The row in which to move the widget (0 is the leftmost column)

        """
        row_span = None
        col_span = None

        for (_, _, rspan, cspan, w) in self._grid_widgets.values():
            if w == widget:
                row_span = rspan
                col_span = cspan
                break

        if row_span is None or col_span is None:
            raise ValueError("%s not found in grid." %
                             (widget, ))

        self.remove_widget(widget)
        self.add_widget(widget, row, col, row_span, col_span)
        self._need_solver_recreate = True

    def _prepare_draw(self, view):
        self._update_child_widget_constraints()

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

    def _update_child_widget_constraints(self):

        if self._need_solver_recreate:
            self._need_solver_recreate = False
            # self._recreate_child_widet_constraints()

        # think in terms of (x, y). (row, col) makes code harder to read
        ymax, xmax = self.grid_size
        if ymax <= 0 or xmax <= 0:
            return

        rect = self.rect.padded(self.padding + self.margin)
        if rect.width <= 0 or rect.height <= 0:
            return

        self._solver = SimplexSolver()

        width_grid = [[Variable("width(x: %s, y: %s)" %
                      (x, y)) for x in range(0, xmax)]
                      for y in range(0, ymax)]

        stretch_widths_grid = np.array([[1 for _ in range(0, xmax)
                                        for _ in range(0, ymax)]], dtype=np.float)

        for (_, val) in self._grid_widgets.items():
            (row, col, rspan, cspan, widget) = val
            (stretch_w, stretch_h) = widget.stretch
            stretch_widths_grid[row:row+rspan, col:col+cspan] = stretch_w

        for (y, ws) in enumerate(width_grid):
            width_expr = expression.Expression()
            print("y: %s, ws: %s" % (y, ws))
            stretch_expr = ws[0] / stretch_widths_grid[y][0] if len(ws) > 0 else None

            for (x, w) in enumerate(ws):
                width_expr = width_expr + w
                if stretch_expr is not None:
                    self._solver.add_constraint(w / float(stretch_widths_grid[y][x])
                                                == stretch_expr)
            self._solver.add_constraint(width_expr == self.var_w)

        height_grid = [[Variable("height(x: %s, y: %s" %
                       (x, y)) for y in range(0, ymax)]
                       for x in range(0, xmax)]

        stretch_height_grid = np.array([[1 for _ in range(0, ymax)]
                                         for _ in range(0, xmax)], dtype=np.float)

        for (_, val) in self._grid_widgets.items():
            (row, col, rspan, cspan, widget) = val
            (stretch_w, stretch_h) = widget.stretch
            stretch_height_grid[col:col+cspan][row:row+rspan] = stretch_h

        for (x, hs) in enumerate(height_grid):
            height_expr = expression.Expression()
            stretch_expr = hs[0] / stretch_height_grid[x][0] if len(hs) > 0 else None

            for (y, h) in enumerate(hs):
                height_expr = height_expr + h
            if stretch_expr is not None:
                self._solver.add_constraint(h / float(stretch_height_grid[x][y])
                                            == stretch_expr)

            self._solver.add_constraint(height_expr == self.var_h)

        self._solver.add_edit_var(self.var_w)
        self._solver.add_stay(self.var_w, rect.width)

        self._solver.add_edit_var(self.var_h)
        self._solver.add_stay(self.var_h, rect.height)

        with self._solver.edit():
                self._solver.suggest_value(self.var_w, int(rect.width))
                self._solver.suggest_value(self.var_h, int(rect.height))

        self._solver.solve()

        print("widths:\n%s" % width_grid)
        print("heights:\n%s" % height_grid)
        # copy dimensions

        value_vectorized = np.vectorize(lambda x: x.value)

        for (_, val) in self._grid_widgets.items():
            (row, col, rspan, cspan, widget) = val

            width = np.sum(value_vectorized(width_grid[row][col:col+cspan]))
            height = np.sum(value_vectorized(height_grid[col][row:row+rspan]))
            if col == 0:
                x = 0
            else:
                x = np.sum(value_vectorized(width_grid[row][0:col]))

            if row == 0:
                y = 0
            else:
                y = np.sum(value_vectorized(height_grid[col][0:row]))
            print("width: %s | height: %s | x: %s | y: %s" % (width, height, x, y))
            widget.size = (width, height)
            widget.pos = (x, y)
