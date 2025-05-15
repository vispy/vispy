# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Grid widget for providing a gridded layout to child widgets."""

from __future__ import division

from typing import Any

import numpy as np
from numpy.typing import NDArray
from collections import defaultdict

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

        self._width_layout = None
        self._height_layout = None

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

    @property
    def spacing(self):
        return self._spacing

    @spacing.setter
    def spacing(self, value):
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
    def _calculate_total_spacing(layout, index, spacing) -> int:
        """Calculate the total amount of spacing a given grid row or column.

        Parameters
        ----------
        layout: dict[int, dict[int, list[int]]
            Either width_layout or height_layout. In case of width_layout, the keys are the rows and the values
            dictionaries with as keys the columns and as values the column spans for Viewboxes assigned to the specific
            grid cell. In case of height_layout, the keys are the columns and the values dictionaries with as keys the
            rows and as values the column spans for Viewboxes assigned to the specific grid cell.
        index: int
            Either the row or column index.
        spacing: float
            The amount of spacing between single adjacent Viewbox widgets in the grid.

        Returns
        -------
        int
            Total amount of spacing for a given column or row.
        """
        return sum(
            spacing
            for value in list(layout[index].values())[:-1]
            if any(span == 1 for span in value)
        )

    @staticmethod
    def _calculate_spacing_offset(layout, index, other_index, spacing) -> int:
        """Calculate the offset due to spacing for the x or y position of Viewbox in grid.

        Parameters
        ----------
        layout: dict[int, dict[int, list[int]]]
            Either width_layout or height_layout. In case of width_layout, the keys are the rows and the values
            dictionaries with as keys the columns and as values the column spans for Viewboxes assigned to the specific
            grid cell. In case of height_layout, the keys are the columns and the values dictionaries with as keys the
            rows and as values the column spans for Viewboxes assigned to the specific grid cell.
        index: int
            Either the row or column index.
        other_index: int
            If index corresponds to row, then other index corresponds to column and vice versa.
        spacing: float
            The amount of spacing between single adjacent Viewbox widgets in the grid.

        Returns
        -------
        int
            Offset due to spacing for the x or y position of Viewbox in grid."""
        return (
            sum(
                spacing
                for subindex in range(index)
                if any(span == 1 for span in layout[other_index][subindex])
            )
            if index != 0
            else 0
        )

    @staticmethod
    def _add_spacing_to_widget_dim_length(layout, index, current_widget_total_span, span, spacing):
        """Add spacing to widget dimension length.

        Spacing has to be added in case 1 Viewbox spans 2 or more Viewboxes that have spacing inbetween them.

        Parameters
        ----------
        layout: dict[int, dict[int, list[int]]]
            Either width_layout or height_layout. In case of width_layout, the keys are the rows and the values
            dictionaries with as keys the columns and as values the column spans for Viewboxes assigned to the specific
            grid cell. In case of height_layout, the keys are the columns and the values dictionaries with as keys the
            rows and as values the column spans for Viewboxes assigned to the specific grid cell.
        index: int
            Either the row or column index. If row index then span corresponds to column span and vice versa.
        current_widget_total_span: int
            Current widget row or col index + span.
        span: int
            The col or row span in the sense of how many columns or rows does the Viewbox span.
        spacing: float
            The amount of spacing between single adjacent Viewbox widgets in the grid.

        Returns
        -------
        increase_spacing: int
            The amount of spacing to add to the widget dim length to properly span the other Viewbox widgets."""
        increase_spacing = 0
        if span > 1:
            for i in range(current_widget_total_span - 1):
                # Use set in order to prevent same cspans adding spacing width twice.
                for widget_span in layout[index][i]:
                    if widget_span + i < current_widget_total_span:
                        increase_spacing += spacing
        return increase_spacing

    @staticmethod
    def _add_total_width_constraints(solver, width_grid, width_layout, _var_w, spacing):
        for row_index, ws in enumerate(width_grid):
            # Width_grid takes every column included in the grid visualization, instead of every view.
            # so we have to set spacing to 0 to prevent spacing when having 1 viewbox, but col_span > 1.
            spacing = 0 if len(width_layout[row_index]) == 1 else spacing
            width_expr = ws[0]
            for w in ws[1:]:
                width_expr += w

            width_expr += Grid._calculate_total_spacing(width_layout, row_index, spacing)
            solver.addConstraint(width_expr == _var_w)

    @staticmethod
    def _add_total_height_constraints(solver, height_grid, height_layout, _var_h, spacing):
        for col_index, hs in enumerate(height_grid):
            spacing = 0 if len(height_layout[col_index]) == 1 else spacing
            height_expr = hs[0]
            for h in hs[1:]:
                height_expr += h

            height_expr += Grid._calculate_total_spacing(height_layout, col_index, spacing)
            solver.addConstraint(height_expr == _var_h)

    @staticmethod
    def _add_gridding_width_constraints(solver: Solver, width_grid: NDArray[Variable]):
        """Add constraint: all widths in each row are equal.

        With all widths the reserved space for a widget with a col_span and row_span of 1 is meant, e.g. we have 3
        widgets arranged in columns with col_span 1 and those are being constrained to all be of width 100.

        Parameters
        ----------
        solver: Solver
            Solver for a system of linear equations.
        height_grid:
            The width grid in shape col * row with each element being a Variable in the solver representing the height
            of each grid box.
        """
        # access widths of one "y", different x
        for ws in width_grid.T:
            for w in ws[1:]:
                solver.addConstraint(ws[0] == w)

    @staticmethod
    def _add_gridding_height_constraints(solver, height_grid):
        """Add constraint: all heights in each column are equal.

        With all heights the reserved space for a widget with a col_span and row_span of 1 is meant, e.g. we have 3
        widgets arranged in rows with col_span 1 and those are being constrained to all be of height 100.

        Parameters
        ----------
        solver: Solver
            Solver for a system of linear equations.
        height_grid:
            The width grid in shape row * col with each element being a Variable in the solver representing the width
            of each grid box.
        """
        # access heights of one "y"
        for hs in height_grid.T:
            for h in hs[1:]:
                solver.addConstraint(hs[0] == h)

    @staticmethod
    def _add_stretch_constraints(solver, width_grid, height_grid, width_layout, height_layout,
                                 grid_widgets, widget_grid, width_spacing, height_spacing):
        xmax = len(height_grid)
        ymax = len(width_grid)

        stretch_widths = [[] for _ in range(ymax)]
        stretch_heights = [[] for _ in range(xmax)]

        for (y, x, ys, xs, widget) in grid_widgets.values():
            for index, ws in enumerate(width_grid[y:y+ys]):
                width_spacing = 0 if index == 0 or all(cspan > 1 for cspan in width_layout[y][index]) else width_spacing
                total_w = np.sum(ws[x:x+xs]) + width_spacing

                for sw in stretch_widths[y:y+ys]:
                    sw.append((total_w, widget.stretch[0]))

            for index, hs in enumerate(height_grid[x:x+xs]):
                height_spacing = 0 if index == len(height_grid) - 1 or all(
                    rspan > 1 for rspan in height_layout[x][index]) else height_spacing
                total_h = np.sum(hs[y:y+ys]) + height_spacing

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
    def _add_widget_dim_constraints(solver, width_grid, height_grid, total_var_w, total_var_h, grid_widgets):
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


        self._width_layout = defaultdict(lambda: defaultdict(list))
        self._height_layout = defaultdict(lambda: defaultdict(list))

        for value in self._grid_widgets.values():
            self._width_layout[value[0]][value[1]].append(value[-2])
            self._height_layout[value[1]][value[0]].append(value[-3])

        # add widths
        self._width_grid = np.array(
            [
                [Variable(f"width(x: {x}, y: {y})") for x in range(0, xmax)]
                for y in range(0, ymax)
            ]
        )

        # add heights
        self._height_grid = np.array(
            [
                [Variable(f"height(x: {x}, y: {y}") for y in range(0, ymax)]
                for x in range(0, xmax)
            ]
        )

        # setup stretch
        stretch_grid = np.zeros(shape=(xmax, ymax, 2), dtype=float)
        stretch_grid.fill(1)

        for (_, val) in self._grid_widgets.items():
            (y, x, ys, xs, widget) = val
            stretch_grid[x:x+xs, y:y+ys] = widget.stretch

        if isinstance(self.spacing, tuple):
            width_spacing, height_spacing = self.spacing
        else:
            width_spacing = height_spacing = self.spacing
        # even though these are REQUIRED, these should never fail
        # since they're added first, and thus the slack will "simply work".
        Grid._add_total_width_constraints(self._solver,
                                          self._width_grid, self._width_layout, self._var_w, width_spacing)
        Grid._add_total_height_constraints(self._solver,
                                           self._height_grid, self._height_layout, self._var_h, height_spacing)

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
                                      self._width_layout,
                                      self._height_layout,
                                      self._grid_widgets,
                                      self._widget_grid,
                                      width_spacing,
                                      height_spacing)

        Grid._add_widget_dim_constraints(self._solver,
                                         self._width_grid,
                                         self._height_grid,
                                         self._var_w,
                                         self._var_h,
                                         self._grid_widgets
                                         )

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

        if isinstance(self.spacing, tuple):
            width_spacing, height_spacing = self.spacing
        else:
            width_spacing = height_spacing = self.spacing

        for index, (_, val) in enumerate(self._grid_widgets.items()):
            (row, col, rspan, cspan, widget) = val

            # To have the proper x or y position we need to know how much spacing has been applied so far. We can't
            # just directly multiply with row or col because of spans potentially being higher than 1.
            spacing_width_offset = Grid._calculate_spacing_offset(self._width_layout, col, row, width_spacing)
            spacing_height_offset = Grid._calculate_spacing_offset(self._height_layout, row, col, height_spacing)

            current_widget_total_cspan = col + cspan
            current_widget_total_rspan = row + rspan

            # We need to check if there is any widget that has a span falling within the range of the current widgets
            # span. For each span range that falls within we need to increase the width.
            width_increase_spacing = Grid._add_spacing_to_widget_dim_length(self._width_layout,
                                                                            row, current_widget_total_cspan,
                                                                            cspan, width_spacing)
            height_increase_spacing = Grid._add_spacing_to_widget_dim_length(self._height_layout, col,
                                                                             current_widget_total_rspan, rspan,
                                                                             height_spacing)

            width = np.sum(value_vectorized(
                           self._width_grid[row][col:col+cspan]) + width_increase_spacing)
            height = np.sum(value_vectorized(
                            self._height_grid[col][row:row+rspan]) + height_increase_spacing)

            if col == 0:
                x = 0
            else:
                x = np.sum(value_vectorized(self._width_grid[row][:col])) + spacing_width_offset

            if row == 0:
                y = 0
            else:
                y = np.sum(value_vectorized(self._height_grid[col][:row])) + spacing_height_offset

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
