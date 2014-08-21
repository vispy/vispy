# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .widget import Widget


class Grid(Widget):
    """
    Widget that automatically sets the position and size of child Widgets to
    proportionally divide its internal area into a grid.
    """
    def __init__(self, **kwds):
        self._next_cell = [0, 0]  # row, col
        self._cells = {}
        self._grid_widgets = {}
        self.spacing = 6
        Widget.__init__(self, **kwds)

    def add_widget(self, widget=None, row=None, col=None, row_span=1, 
                   col_span=1):
        """
        Add a new widget to this grid.
        """
        if row is None:
            row = self._next_cell[0]
        if col is None:
            col = self._next_cell[1]

        if widget is None:
            widget = Widget()

        _row = self._cells.setdefault(row, {})
        _row[col] = widget
        self._grid_widgets[widget] = row, col, row_span, col_span
        widget.add_parent(self)

        self._next_cell = [row, col+col_span]
        self._update_child_widgets()
        return widget

    def next_row(self):
        self._next_cell = [self._next_cell[0] + 1, 0]

    def _update_child_widgets(self):
        # Resize all widgets in this grid to share space.
        # This logic will need a lot of work..

        rvals = [widget[0]+widget[2] for widget in self._grid_widgets.values()]
        cvals = [widget[1]+widget[3] for widget in self._grid_widgets.values()]
        if len(rvals) == 0 or len(cvals) == 0:
            return

        nrows = max(rvals)
        ncols = max(cvals)

        # determine starting/ending position of each row and column
        s2 = self.spacing / 2.
        rect = self.rect.padded(self.padding + self.margin - s2)
        rows = np.linspace(rect.bottom, rect.top, nrows+1)
        rowstart = rows[:-1] + s2
        rowend = rows[1:] - s2
        cols = np.linspace(rect.left, rect.right, ncols+1)
        colstart = cols[:-1] + s2
        colend = cols[1:] - s2

        for ch in self._grid_widgets:
            row, col, rspan, cspan = self._grid_widgets[ch]

            # Translate the origin of the entity to the corner of the area
            #ch.transform.reset()
            #ch.transform.translate((colstart[col], rowstart[row]))
            ch.pos = colstart[col], rowstart[row]

            # ..and set the size to match.
            w = colend[col+cspan-1]-colstart[col]
            h = rowend[row+rspan-1]-rowstart[row]
            ch.size = w, h
