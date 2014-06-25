# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division



class GridBox(Box):
    """
    Box that automatically sets the position and size of child Boxes to
    proportionally divide its internal area into a grid.
    """
    def __init__(self, parent=None, pos=None, size=None, border=None):
        Box.__init__(self, parent, pos, size, border)
        self._next_cell = [0, 0]  # row, col
        self._cells = {}
        self._boxes = {}
        self.spacing = 6

    def add_box(self, box=None, row=None, col=None, row_span=1, col_span=1):
        """
        Add a new box to this grid.
        """
        if row is None:
            row = self._next_cell[0]
        if col is None:
            col = self._next_cell[1]

        if box is None:
            box = Box()

        _row = self._cells.setdefault(row, {})
        _row[col] = box
        self._boxes[box] = row, col, row_span, col_span
        box.add_parent(self)

        self._next_cell = [row, col+col_span]
        self._update_child_boxes()
        return box

    def next_row(self):
        self._next_cell = [self._next_cell[0] + 1, 0]

    def _update_child_boxes(self):
        # Resize all boxes in this grid to share space.
        # This logic will need a lot of work..

        rvals = [box[0]+box[2] for box in self._boxes.values()]
        cvals = [box[1]+box[3] for box in self._boxes.values()]
        if len(rvals) == 0 or len(cvals) == 0:
            return

        nrows = max(rvals)
        ncols = max(cvals)

        # determine starting/ending position of each row and column
        s2 = self.spacing / 2.
        rect = self.rect.padded(self.padding + self.margin - s2)
        rows = np.linspace(rect.top, rect.bottom, nrows+1)
        rowstart = rows[1:] + s2
        rowend = rows[:-1] - s2
        cols = np.linspace(rect.left, rect.right, ncols+1)
        colstart = cols[:-1] + s2
        colend = cols[1:] - s2

        for ch in self._boxes:
            row, col, rspan, cspan = self._boxes[ch]

            # Translate the origin of the entity to the corner of the area
            ch.transform.reset()
            ch.transform.translate((colstart[col], rowstart[row]))

            # ..and set the size to match.
            w = colend[col+cspan-1]-colstart[col]
            h = rowend[row+rspan-1]-rowstart[row]
            ch.size = w, h
