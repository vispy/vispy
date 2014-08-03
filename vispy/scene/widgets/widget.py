# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from ..visuals.visual import Visual
from ..visuals.line import Line
from ..transforms import STTransform
from ...util.event import Event
from ...util.geometry import Rect
from ...color import Color


class Widget(Visual):
    """ A widget takes up a rectangular space, intended for use in
    a 2D pixel coordinate frame.

    The widget is positioned using the transform attribute (as any
    entity), and its extend (size) is kept as a separate property.
    """

    def __init__(self, *args, **kwargs):
        self._border = kwargs.pop('border', (0.2, 0.2, 0.2, 0.5))
        # for drawing border
        self._visual = Line(color=self._border)
        # whether this widget should clip its children
        self._clip = kwargs.pop('clip', False)
        # reserved space inside border
        self._padding = kwargs.pop('padding', 0)
        # reserved space outside border
        self._margin = kwargs.pop('margin', 0)
        
        pos = kwargs.pop('pos', (0, 0))
        size = kwargs.pop('size', (10, 10))
        
        Visual.__init__(self, *args, **kwargs)
        self.events.add(rect_change=Event)
        self._size = 16, 16
        self.transform = STTransform()
        # todo: TTransform (translate only for widgets)

        self._widgets = []
        self.pos = pos
        self.size = size

    @property
    def pos(self):
        return tuple(self.transform.translate[:2])

    @pos.setter
    def pos(self, p):
        assert isinstance(p, tuple)
        assert len(p) == 2
        self.transform.translate = p[0], p[1], 0, 0
        self._update_line()
        self.events.rect_change()

    @property
    def size(self):
        # Note that we cannot let the size be reflected in the transform.
        # Consider a widget of 40x40 in a pixel grid, a child widget therin
        # with size 20x20 would get a scale of 800x800!
        return self._size

    @size.setter
    def size(self, s):
        assert isinstance(s, tuple)
        assert len(s) == 2
        self._size = s
        self._update_line()
        self.events.rect_change()
        self._update_child_widgets()

    @property
    def rect(self):
        return Rect((0, 0), self.size)

    @rect.setter
    def rect(self, r):
        with self.events.rect_change.blocker():
            self.pos = r.pos
            self.size = r.size
        self.update()
        self.events.rect_change()

    @property
    def border(self):
        return self._border

    @border.setter
    def border(self, b):
        self._border = b
        self._visual.set_data(color=b)
        self.update()

    @property
    def background(self):
        """ The background color of the Widget.
        """
        return self._background

    @background.setter
    def background(self, value):
        self._background = Color(value)
        self.update()

    @property
    def margin(self):
        return self._margin

    @margin.setter
    def margin(self, m):
        self._margin = m
        self._update_line()

    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, p):
        self._padding = p
        self._update_child_boxes()

    def _update_line(self):
        """ Update border line to match new shape """
        m = self.margin
        r = self.size[0] - m
        t = self.size[1] - m
        
        pos = np.array([
            [m, m],
            [r, m],
            [r, t],
            [m, t],
            [m, m]]).astype(np.float32)
        self._visual.set_data(pos=pos)

    def draw(self, event):
        self._visual.draw(event)

    def on_rect_change(self, ev):
        self._update_child_widgets()

    def _update_child_widgets(self):
        # Set the position and size of child boxes (only those added
        # using add_widget)
        for ch in self._widgets:
            ch.rect = self.rect.padded(self.padding + self.margin)

    def add_widget(self, widget):
        """
        Add a Widget as a managed child of this Widget. The child will be
        automatically positioned and sized to fill the entire space inside
        this Widget (unless _update_child_widgets is redefined).
        """
        self._widgets.append(widget)
        widget.parent = self
        self._update_child_widgets()
        return widget

    def add_grid(self, *args, **kwds):
        """
        Create a new Grid and add it as a child widget.

        All arguments are given to add_widget().
        """
        from .grid import Grid
        grid = Grid()
        return self.add_widget(grid, *args, **kwds)

    def add_view(self, *args, **kwds):
        """
        Create a new ViewBox and add it as a child widget.

        All arguments are given to add_widget().
        """
        from .viewbox import ViewBox
        view = ViewBox()
        return self.add_widget(view, *args, **kwds)

    def remove_widget(self, widget):
        self._widgets.remove(widget)
        widget.remove_parent(self)
        self._update_child_widgets()
