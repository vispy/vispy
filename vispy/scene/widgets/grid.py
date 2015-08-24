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
            self._recreate_child_widet_constraints()

        rect = self.rect.padded(self.padding + self.margin)

        if rect.width <= 0 or rect.height <= 0:
            return

        self._solver.add_edit_var(self.var_w)
        self._solver.add_edit_var(self.var_h)

        with self._solver.edit():
                self._solver.suggest_value(self.var_w, rect.width)
                self._solver.suggest_value(self.var_h, rect.height)

        # copy dimensions
        for (_, val) in self._grid_widgets.items():
            (row, col, rspan, cspan, widget) = val
            widget.size = (widget.var_w.value, widget.var_h.value)
            widget.pos = (widget.var_x.value, widget.var_y.value)

    def _recreate_child_widet_constraints(self):
        # Resize all widgets in this grid to share space.
        n_rows, n_cols = self.grid_size
        if n_rows == 0 or n_cols == 0:
            return

        rect = self.rect.padded(self.padding + self.margin)

        if rect.width <= 0 or rect.height <= 0:
            return

        self._solver = SimplexSolver()
        self._solver.add_stay(self.var_w)
        self._solver.add_stay(self.var_h)

        # x, width constraints ------
        width_slop = Variable("width_slop")
        width_slop.value = 0
        self._solver.add_stay(width_slop, strength=STRONG)

        height_slop = Variable("height_slop")
        height_slop.value = 0
        self._solver.add_stay(height_slop, strength=STRONG)

        w_total_eqns = [expression.Expression(width_slop)
                        for _ in range(0, n_rows)]
        h_total_eqns = [expression.Expression(height_slop)
                        for _ in range(0, n_cols)]

        w_stretch_terms = [[] for _ in range(0, n_rows)]
        h_stretch_terms = [[] for _ in range(0, n_cols)]

        for _, value in self._grid_widgets.items():
            (row, col, rspan, cspan, widget) = value

            # dimensions
            for w_eqn in w_total_eqns[row:row+rspan]:
                    w_eqn.add_expression(widget.var_w)

            for h_eqn in h_total_eqns[col:col+cspan]:
                    h_eqn.add_expression(widget.var_h)

            assert(widget.width_min is not None)
            self._solver.add_constraint(widget.var_w >= widget.width_min)

            if widget.width_max is not None:
                self._solver.add_constraint(widget.var_w <= widget.width_max)

            assert(widget.height_min is not None)
            self._solver.add_constraint(widget.var_h >= widget.height_min)

            if widget.height_max is not None:
                self._solver.add_constraint(widget.var_h <= widget.height_max)

            if widget.stretch[0] is not None:  # and widget.width_max is None:
                for terms_arr in w_stretch_terms[row:row+rspan]:
                    terms_arr.append(widget.var_w / float(widget.stretch[0]))

            if widget.stretch[1] is not None:  # and widget.height_max is None:
                for terms_arr in h_stretch_terms[col:col+cspan]:
                    terms_arr.append(widget.var_h / float(widget.stretch[1]))

            # x axis pos
            if col == 0:
                widget.var_x.value = rect.left
                self._solver.add_stay(widget.var_x, strength=REQUIRED)
            else:
                prev_widget_id = self.layout_array[row][col - 1]
                if prev_widget_id != -1:
                    prev_widget = self._grid_widgets[prev_widget_id][-1]
                    if prev_widget is not None:
                        self._solver.add_constraint(widget.var_x ==
                                                    prev_widget.var_x +
                                                    prev_widget.var_w)

            # y axis pos
            if row == 0:
                widget.var_y.value = rect.bottom
                self._solver.add_stay(widget.var_y)
            else:
                prev_widget_id = self.layout_array[row - 1][col]
                if prev_widget_id != -1:
                    prev_widget = self._grid_widgets[prev_widget_id][-1]

                    if prev_widget is not None:
                        self._solver.add_constraint(widget.var_y ==
                                                    prev_widget.var_y +
                                                    prev_widget.var_h)

        # set total width, height eqns
        for row, w_eqn in enumerate(w_total_eqns):
            if len(w_eqn.terms) > 0:
                cols_in_row = len(set([l for l in self.layout_array[row]
                                       if l != -1]))
                self._solver.add_constraint(w_eqn ==
                                            self.var_w,
                                            strength=REQUIRED)
        for col, h_eqn in enumerate(h_total_eqns):
            if len(h_eqn.terms) > 0:
                rows_in_col = len(set([l for l in self.layout_array.T[col]
                                       if l != -1]))

                self._solver.add_constraint(h_eqn == self.var_h,
                                            strength=REQUIRED)

        # add stretch eqns
        for terms_arr in w_stretch_terms:
            if len(terms_arr) > 1:
                for term in terms_arr[1:]:
                    self._solver.add_constraint(term == terms_arr[0],
                                                strength=WEAK)

        for terms_arr in h_stretch_terms:
            if len(terms_arr) > 1:
                for term in terms_arr[1:]:
                    self._solver.add_constraint(term == terms_arr[0],
                                                strength=WEAK)
