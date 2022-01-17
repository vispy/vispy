# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Grid widget for providing a gridded layout to child widgets."""

from __future__ import division
import numpy as np

from vispy.geometry import Rect
from .widget import Widget
from .viewbox import ViewBox

from kiwisolver import Solver, Variable, UnsatisfiableConstraint


class Grid(Widget):
    """Widget for proportionally dividing its internal area into a grid.

    This widget will automatically set the position and size of child widgets
    according to provided constraints.

    Parameters
    ----------
    spacing : int
        Spacing between widgets.
    **kwargs : dict
        Keyword arguments to pass to `Widget`.
    """

    def __init__(self, spacing=6, **kwargs):
        """Create solver and basic grid parameters."""
        self._next_cell = [0, 0]  # row, col
        self._cells = {}
        self._grid_widgets = {}
        self.spacing = spacing
        self._n_added = 0
        self._default_class = ViewBox  # what to add when __getitem__ is used
        self._solver = Solver()
        self._need_solver_recreate = True

        # width and height of the Rect used to place child widgets
        self._var_w = Variable("w_rect")
        self._var_h = Variable("h_rect")

        self._width_grid = None
        self._height_grid = None

        # self._height_stay = None
        # self._width_stay = None

        Widget.__init__(self, **kwargs)

    def __getitem__(self, idxs):
        """Return an item or create it if the location is available."""
        if not isinstance(idxs, tuple):
            idxs = (idxs,)
        if len(idxs) == 1:
            idxs = idxs + (slice(0, 1, None),)
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
                   col_span=1, **kwargs):
        """Add a new widget to this grid.

        This will cause other widgets in the grid to be resized to make room
        for the new widget. Can be used to replace a widget as well.

        Parameters
        ----------
        widget : Widget | None
            The Widget to add. New widget is constructed if widget is None.
        row : int
            The row in which to add the widget (0 is the topmost row)
        col : int
            The column in which to add the widget (0 is the leftmost column)
        row_span : int
            The number of rows to be occupied by this widget. Default is 1.
        col_span : int
            The number of columns to be occupied by this widget. Default is 1.
        **kwargs : dict
            parameters sent to the new Widget that is constructed if
            widget is None

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
            widget = Widget(**kwargs)
        else:
            if kwargs:
                raise ValueError("cannot send kwargs if widget is given")

        _row = self._cells.setdefault(row, {})
        _row[col] = widget
        self._grid_widgets[self._n_added] = (row, col, row_span, col_span,
                                             widget)
        self._n_added += 1
        widget.parent = self

        self._next_cell = [row, col+col_span]

        widget._var_w = Variable("w-(row: %s | col: %s)" % (row, col))
        widget._var_h = Variable("h-(row: %s | col: %s)" % (row, col))

        # update stretch based on colspan/rowspan
        # usually, if you make something consume more grids or columns,
        # you also want it to actually *take it up*, ratio wise.
        # otherwise, it will never *use* the extra rows and columns,
        # thereby collapsing the extras to 0.
        stretch = list(widget.stretch)
        stretch[0] = col_span if stretch[0] is None else stretch[0]
        stretch[1] = row_span if stretch[1] is None else stretch[1]
        widget.stretch = stretch

        self._need_solver_recreate = True

        return widget

    def remove_widget(self, widget):
        """Remove a widget from this grid.

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

        for (r, c, _rspan, _cspan, w) in self._grid_widgets.values():
            if w == widget:
                row = r
                col = c

                break

        if row is None or col is None:
            raise ValueError("%s not found in grid" % widget)

        self.remove_widget(widget)
        self.add_widget(widget, row, col, row_span, col_span)
        self._need_solver_recreate = True

    def _prepare_draw(self, view):
        self._update_child_widget_dim()

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

    @staticmethod
    def _add_total_width_constraints(solver, width_grid, _var_w):
        for ws in width_grid:
            width_expr = ws[0]
            for w in ws[1:]:
                width_expr += w
            solver.addConstraint(width_expr == _var_w)

    @staticmethod
    def _add_total_height_constraints(solver, height_grid, _var_h):
        for hs in height_grid:
            height_expr = hs[0]
            for h in hs[1:]:
                height_expr += h
            solver.addConstraint(height_expr == _var_h)

    @staticmethod
    def _add_gridding_width_constraints(solver, width_grid):
        # access widths of one "y", different x
        for ws in width_grid.T:
            for w in ws[1:]:
                solver.addConstraint(ws[0] == w)

    @staticmethod
    def _add_gridding_height_constraints(solver, height_grid):
        # access heights of one "y"
        for hs in height_grid.T:
            for h in hs[1:]:
                solver.addConstraint(hs[0] == h)

    @staticmethod
    def _add_stretch_constraints(solver, width_grid, height_grid,
                                 grid_widgets, widget_grid):
        xmax = len(height_grid)
        ymax = len(width_grid)

        stretch_widths = [[] for _ in range(0, ymax)]
        stretch_heights = [[] for _ in range(0, xmax)]

        for (y, x, ys, xs, widget) in grid_widgets.values():
            for ws in width_grid[y:y+ys]:
                total_w = np.sum(ws[x:x+xs])

                for sw in stretch_widths[y:y+ys]:
                    sw.append((total_w, widget.stretch[0]))

            for hs in height_grid[x:x+xs]:
                total_h = np.sum(hs[y:y+ys])

                for sh in stretch_heights[x:x+xs]:
                    sh.append((total_h, widget.stretch[1]))

        for (x, xs) in enumerate(widget_grid):
            for(y, widget) in enumerate(xs):
                if widget is None:
                    stretch_widths[y].append((width_grid[y][x], 1))
                    stretch_heights[x].append((height_grid[x][y], 1))

        for sws in stretch_widths:
            if len(sws) <= 1:
                continue

            comparator = sws[0][0] / sws[0][1]

            for (stretch_term, stretch_val) in sws[1:]:
                solver.addConstraint((comparator == stretch_term/stretch_val) |
                                     'weak')

        for sws in stretch_heights:
            if len(sws) <= 1:
                continue

            comparator = sws[0][0] / sws[0][1]

            for (stretch_term, stretch_val) in sws[1:]:
                solver.addConstraint((comparator == stretch_term/stretch_val) |
                                     'weak')

    @staticmethod
    def _add_widget_dim_constraints(solver, width_grid, height_grid,
                                    total_var_w, total_var_h, grid_widgets):
        assert(total_var_w is not None)
        assert(total_var_h is not None)

        for ws in width_grid:
            for w in ws:
                solver.addConstraint(w >= 0,)

        for hs in height_grid:
            for h in hs:
                solver.addConstraint(h >= 0)

        for (_, val) in grid_widgets.items():
            (y, x, ys, xs, widget) = val

            for ws in width_grid[y:y+ys]:
                total_w = np.sum(ws[x:x+xs])
                # assert(total_w is not None)
                solver.addConstraint(total_w >= widget.width_min)

                if widget.width_max is not None:
                    solver.addConstraint(total_w <= widget.width_max)
                else:
                    solver.addConstraint(total_w <= total_var_w)

            for hs in height_grid[x:x+xs]:
                total_h = np.sum(hs[y:y+ys])
                solver.addConstraint(total_h >= widget.height_min)

                if widget.height_max is not None:
                    solver.addConstraint(total_h <= widget.height_max)
                else:
                    solver.addConstraint(total_h <= total_var_h)

    def _recreate_solver(self):
        self._solver.reset()
        self._var_w = Variable("w_rect")
        self._var_h = Variable("h_rect")
        self._solver.addEditVariable(self._var_w, 'strong')
        self._solver.addEditVariable(self._var_h, 'strong')

        rect = self.rect.padded(self.padding + self.margin)
        ymax, xmax = self.grid_size

        self._solver.suggestValue(self._var_w, rect.width)
        self._solver.suggestValue(self._var_h, rect.height)

        self._solver.addConstraint(self._var_w >= 0)
        self._solver.addConstraint(self._var_h >= 0)

        # self._height_stay = None
        # self._width_stay = None

        # add widths
        self._width_grid = np.array([[Variable("width(x: %s, y: %s)" % (x, y))
                                      for x in range(0, xmax)]
                                     for y in range(0, ymax)])

        # add heights
        self._height_grid = np.array([[Variable("height(x: %s, y: %s" % (x, y))
                                       for y in range(0, ymax)]
                                      for x in range(0, xmax)])

        # setup stretch
        stretch_grid = np.zeros(shape=(xmax, ymax, 2), dtype=float)
        stretch_grid.fill(1)

        for (_, val) in self._grid_widgets.items():
            (y, x, ys, xs, widget) = val
            stretch_grid[x:x+xs, y:y+ys] = widget.stretch

        # even though these are REQUIRED, these should never fail
        # since they're added first, and thus the slack will "simply work".
        Grid._add_total_width_constraints(self._solver,
                                          self._width_grid, self._var_w)
        Grid._add_total_height_constraints(self._solver,
                                           self._height_grid, self._var_h)

        try:
            # these are REQUIRED constraints for width and height.
            # These are the constraints which can fail if
            # the corresponding dimension of the widget cannot be fit in the
            # grid.
            Grid._add_gridding_width_constraints(self._solver,
                                                 self._width_grid)
            Grid._add_gridding_height_constraints(self._solver,
                                                  self._height_grid)
        except UnsatisfiableConstraint:
            self._need_solver_recreate = True

        # these are WEAK constraints, so these constraints will never fail
        # with a RequiredFailure.
        Grid._add_stretch_constraints(self._solver,
                                      self._width_grid,
                                      self._height_grid,
                                      self._grid_widgets,
                                      self._widget_grid)

        Grid._add_widget_dim_constraints(self._solver,
                                         self._width_grid,
                                         self._height_grid,
                                         self._var_w,
                                         self._var_h,
                                         self._grid_widgets)

        self._solver.updateVariables()

    def _update_child_widget_dim(self):
        # think in terms of (x, y). (row, col) makes code harder to read
        ymax, xmax = self.grid_size
        if ymax <= 0 or xmax <= 0:
            return

        rect = self.rect  # .padded(self.padding + self.margin)
        if rect.width <= 0 or rect.height <= 0:
            return
        if self._need_solver_recreate:
            self._need_solver_recreate = False
            self._recreate_solver()

        # we only need to remove and add the height and width constraints of
        # the solver if they are not the same as the current value
        h_changed = abs(rect.height - self._var_h.value()) > 1e-4
        w_changed = abs(rect.width - self._var_w.value()) > 1e-4
        if h_changed:
            self._solver.suggestValue(self._var_h, rect.height)

        if w_changed:
            self._solver.suggestValue(self._var_w, rect.width)
        if h_changed or w_changed:
            self._solver.updateVariables()

        value_vectorized = np.vectorize(lambda x: x.value())

        for (_, val) in self._grid_widgets.items():
            (row, col, rspan, cspan, widget) = val

            width = np.sum(value_vectorized(
                           self._width_grid[row][col:col+cspan]))
            height = np.sum(value_vectorized(
                            self._height_grid[col][row:row+rspan]))
            if col == 0:
                x = 0
            else:
                x = np.sum(value_vectorized(self._width_grid[row][0:col]))

            if row == 0:
                y = 0
            else:
                y = np.sum(value_vectorized(self._height_grid[col][0:row]))

            if isinstance(widget, ViewBox):
                widget.rect = Rect(x, y, width, height)
            else:
                widget.size = (width, height)
                widget.pos = (x, y)

    @property
    def _widget_grid(self):
        ymax, xmax = self.grid_size
        widget_grid = np.array([[None for _ in range(0, ymax)]
                                for _ in range(0, xmax)])
        for (_, val) in self._grid_widgets.items():
            (y, x, ys, xs, widget) = val
            widget_grid[x:x+xs, y:y+ys] = widget

        return widget_grid
