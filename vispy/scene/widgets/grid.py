# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Grid widget for providing a gridded layout to child widgets."""

from __future__ import division

from typing import Tuple, Union, Dict

import numpy as np
from numpy.typing import NDArray

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
    spacing : int | tuple[int, int]
        Spacing between widgets. If `tuple` then it must be of length two, the first element
        being `width_spacing` and the second being `height_spacing`.
    **kwargs : dict
        Keyword arguments to pass to `Widget`.
    """

    def __init__(self, spacing=0, **kwargs):
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

    @property
    def spacing(self):
        """
        The spacing between individual Viewbox widgets in the grid.
        """
        return self._spacing

    @spacing.setter
    def spacing(self, value: Union[int, Tuple[int, int]]):
        if not (
            isinstance(value, int)
            or isinstance(value, tuple)
            and len(value) == 2
            and isinstance(value[0], int)
            and isinstance(value[1], int)
        ):
            raise ValueError('spacing must be of type int | tuple[int, int]')

        self._spacing = value
        self._need_solver_recreate = True

    def __repr__(self):
        return (('<Grid at %s:\n' % hex(id(self))) +
                str(self.layout_array + 1) + '>')

    @staticmethod
    def _add_total_dim_length_constraints(solver: Solver, grid_dim_variables: NDArray[Variable],
                                          n_added: int, _var_dim_length: Variable, spacing: float):
        """Add constraint: total height == sum(col heights) + sum(spacing).

        The total height of the grid is constrained to be equal to the sum of the heights of
        its columns, including spacing between widgets.

        Parameters
        ----------
        solver: Solver
            Solver for a system of linear equations.
        grid_dim_variables: NDArray[Variable]:
            The grid of width or height variables of either shape col * row or row * col with each element being a
            Variable in the solver representing the height or width of each grid box.
        n_added: int
            The number of ViewBoxes added to the grid.
        _var_dim_length: Variable
            The solver variable representing either total width or height of the grid.
        spacing: float
            The amount of spacing between single adjacent Viewbox widgets in the grid.
        """
        total_spacing = 0
        if n_added > 1:
            for _ in range(grid_dim_variables.shape[1] - 1):
                total_spacing += spacing

        for ds in grid_dim_variables:
            dim_length_expr = ds[0]
            for d in ds[1:]:
                dim_length_expr += d
            dim_length_expr += total_spacing
            solver.addConstraint(dim_length_expr == _var_dim_length)

    @staticmethod
    def _add_gridding_dim_constraints(solver: Solver, grid_dim_variables: NDArray[Variable]):
        """Add constraint: all viewbox dims in each dimension are equal.

        With all dims the reserved space for a widget with a col_span and row_span of 1 is meant, e.g. we have 3
        widgets arranged in columns or rows with col_span or row_span 1 and those are being constrained to all be of
        width/height 100. In other words the same dim length is reserved for each position in the grid, not taking
        into account the spacing between grid positions.

        Parameters
        ----------
        solver: Solver
            Solver for a system of linear equations.
        grid_dim_variables:
            The grid of width or height variables of either shape col * row or row * col with each element being a
            Variable in the solver representing the height or width of each grid box.
        """
        # access widths of one "y", different x
        for ds in grid_dim_variables.T:
            for d in ds[1:]:
                solver.addConstraint(ds[0] == d)

    @staticmethod
    def _add_stretch_constraints(solver: Solver, width_grid: NDArray[Variable] , height_grid: NDArray[Variable],
                                 grid_widgets: Dict[int, Tuple[int, int, int, int, ViewBox]],
                                 widget_grid: NDArray[ViewBox]):
        """
        Add proportional stretch constraints to the linear system solver of the grid.

        This method enforces that grid rows and columns stretch in proportion
        to the widgets' specified stretch factors. It uses weak constraints
        so that proportionality is preserved when possible but can be violated
        if stronger layout constraints are present.

        Parameters
        ----------
        solver : Solver
            Solver for a system of linear equations.
        width_grid : NDArray[Variable]
            The grid of width variables in the linear system of equations to be solved.
        height_grid : NDArray[Variable]
            The grid of height variables in the linear system of equations to be solved.
        grid_widgets : dict[int, tuple[int, int, int, int, ViewBox]]
            Dictionary mapping order of viewboxes added as int to their grid layout description:
            (start_y, start_x, span_y, span_x, ViewBox).
        widget_grid : NDArray[ViewBox]
            Array of viewboxes in shape n_columns x n_rows.

        Notes
        -----
        - Stretch constraints are added with 'weak' strength, allowing them to
          be overridden by stronger constraints such as fixed sizes or min/max bounds.
        - The constraint `total_size / stretch_factor` is used to maintain
          proportional relationships among rows and columns.
        """
        xmax = len(height_grid)
        ymax = len(width_grid)

        stretch_widths = [[] for _ in range(ymax)]
        stretch_heights = [[] for _ in range(xmax)]

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
    def _add_widget_dim_constraints(solver: Solver, width_grid: NDArray[Variable], height_grid: NDArray[Variable],
                                    total_var_w: Variable, total_var_h: Variable,
                                    grid_widgets: Dict[int, Tuple[int, int, int, int, ViewBox]]):
        """Add constraints based on min/max width/height of widgets.

        These constraints ensure that each widget's dimensions stay within its
        specified minimum and maximum values.

        Parameters
        ----------
        solver : Solver
            Solver for a system of linear equations.
        width_grid : NDArray[Variable]
            The grid of width variables in the linear system of equations to be solved.
        height_grid : NDArray[Variable]
            The grid of height variables in the linear system of equations to be solved.
        total_var_w : Variable
            The Variable representing the total width of the grid in the linear system of equations.
        total_var_w : Variable
            The Variable representing the total height of the grid in the linear system of equations.
        grid_widgets : dict[int, tuple[int, int, int, int, ViewBox]]
            Dictionary mapping order of viewboxes added as int to their grid layout description:
            (start_y, start_x, span_y, span_x, ViewBox).
                """
        assert(total_var_w is not None)
        assert(total_var_h is not None)

        for ws in width_grid:
            for w in ws:
                solver.addConstraint(w >= 0)

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
        """Recreate the linear system solver with all constraints."""
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

        # add widths
        self._width_grid = np.array(
            [
                [Variable(f"width(x: {x}, y: {y})") for x in range(xmax)]
                for y in range(ymax)
            ]
        )

        # add heights
        self._height_grid = np.array(
            [
                [Variable(f"height(x: {x}, y: {y})") for y in range(ymax)]
                for x in range(xmax)
            ]
        )

        if isinstance(self.spacing, tuple):
            width_spacing, height_spacing = self.spacing
        else:
            width_spacing = height_spacing = self.spacing
        # even though these are REQUIRED, these should never fail
        # since they're added first, and thus the slack will "simply work".
        Grid._add_total_dim_length_constraints(self._solver,
                                          self._width_grid, self._n_added, self._var_w, width_spacing)
        Grid._add_total_dim_length_constraints(self._solver,
                                           self._height_grid, self._n_added, self._var_h, height_spacing)

        try:
            # these are REQUIRED constraints for width and height.
            # These are the constraints which can fail if
            # the corresponding dimension of the widget cannot be fit in the
            # grid.
            Grid._add_gridding_dim_constraints(self._solver, self._width_grid)
            Grid._add_gridding_dim_constraints(self._solver, self._height_grid)
        except UnsatisfiableConstraint:
            self._need_solver_recreate = True

        # these are WEAK constraints, so these constraints will never fail
        # with a RequiredFailure.
        Grid._add_stretch_constraints(self._solver,
                                      self._width_grid,
                                      self._height_grid,
                                      self._grid_widgets,
                                      self._widget_grid,
                                      )

        Grid._add_widget_dim_constraints(self._solver,
                                         self._width_grid,
                                         self._height_grid,
                                         self._var_w,
                                         self._var_h,
                                         self._grid_widgets
                                         )

        self._solver.updateVariables()

    def _update_child_widget_dim(self):
        """Solve the linear system of equations in order to assign Viewbox parameters such as position."""
        # think in terms of (x, y). (row, col) makes code harder to read
        ymax, xmax = self.grid_size
        if ymax <= 0 or xmax <= 0:
            return

        rect = self.rect.padded(self.padding + self.margin)
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

        if isinstance(self.spacing, tuple):
            width_spacing, height_spacing = self.spacing
        else:
            width_spacing = height_spacing = self.spacing

        for index, (_, val) in enumerate(self._grid_widgets.items()):
            (row, col, rspan, cspan, widget) = val

            # If spacing, always one spacing unit between 2 grid positions, even when span is > 1.
            # If span is > 1, spacing will be added to the dim length of Viewbox
            spacing_width_offset = col * width_spacing if self._n_added > 1 else 0
            spacing_height_offset = row * height_spacing if self._n_added > 1 else 0

            # Add one spacing unit to dim length of the Viewbox per grid positions the ViewBox spans if span > 1.
            width_increase_spacing = width_spacing * (cspan - 1)
            height_increase_spacing = height_spacing * (rspan - 1)

            width = np.sum(value_vectorized(
                           self._width_grid[row][col:col+cspan])) + width_increase_spacing
            height = np.sum(value_vectorized(
                            self._height_grid[col][row:row+rspan])) + height_increase_spacing

            if col == 0:
                x = 0
            else:
                x = np.sum(value_vectorized(self._width_grid[row][:col])) + spacing_width_offset

            if row == 0:
                y = 0
            else:
                y = np.sum(value_vectorized(self._height_grid[col][:row])) + spacing_height_offset

            x += self.padding
            y += self.padding

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
