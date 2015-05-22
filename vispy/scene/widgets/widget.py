# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from ..node import Node
from ...visuals.mesh import MeshVisual
from ...visuals.transforms import STTransform
from ...util.event import Event
from ...geometry import Rect
from ...color import Color


class Widget(Node):
    """ A widget takes up a rectangular space, intended for use in
    a 2D pixel coordinate frame.

    The widget is positioned using the transform attribute (as any
    node), and its extent (size) is kept as a separate property.

    Parameters
    ----------
    pos : (x, y)
        A 2-element tuple to specify the top left corner of the widget.
    size : (w, h)
        A 2-element tuple to spicify the size of the widget.
    border_color : color
        The color of the border.
    bgcolor : color
        The background color.
    clip : bool
        Not used :)
    padding : int
        The amount of padding in the widget (i.e. the space reserved between
        the contents and the border).
    margin : int
        The margin to keep outside the widget's border.
    """

    def __init__(self, pos=(0, 0), size=(10, 10), border_color=None,
                 bgcolor=None, clip=False, padding=0, margin=0, **kwargs):
        Node.__init__(self, **kwargs)

        # For drawing border.
        # A mesh is required because GL lines cannot be drawn with predictable
        # shape across all platforms.
        self._border_color = self._bgcolor = Color(None)
        self._face_colors = None
        self._visual = MeshVisual(mode='triangles')
        self._visual.set_gl_state('translucent', depth_test=False)

        # whether this widget should clip its children
        # (todo)
        self._clip = clip

        # reserved space inside border
        self._padding = padding

        # reserved space outside border
        self._margin = margin

        self.events.add(resize=Event)
        self._size = 16, 16
        self.transform = STTransform()
        # todo: TTransform (translate only for widgets)

        self._widgets = []
        self.pos = pos
        self.size = size
        self.border_color = border_color
        self.bgcolor = bgcolor

    @property
    def pos(self):
        return tuple(self.transform.translate[:2])

    @pos.setter
    def pos(self, p):
        assert isinstance(p, tuple)
        assert len(p) == 2
        if p == self.pos:
            return
        self.transform.translate = p[0], p[1], 0, 0
        self._update_line()
        #self.events.resize()

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
        if self._size == s:
            return
        self._size = s
        self._update_line()
        self.events.resize()
        self._update_child_widgets()

    @property
    def rect(self):
        return Rect((0, 0), self.size)

    @rect.setter
    def rect(self, r):
        with self.events.resize.blocker():
            self.pos = r.pos
            self.size = r.size
        self.update()
        self.events.resize()

    @property
    def inner_rect(self):
        """The rectangular area inside the margin, border and padding.

        Generally widgets should avoid drawing or placing widgets outside this
        rectangle.
        """
        m = self.margin + self.padding
        if not self.border_color.is_blank:
            m += 1
        return Rect((m, m), (self.size[0]-2*m, self.size[1]-2*m))

    @property
    def border_color(self):
        """ The color of the border.
        """
        return self._border_color

    @border_color.setter
    def border_color(self, b):
        self._border_color = Color(b)
        self._update_colors()
        self._update_line()
        self.update()

    @property
    def bgcolor(self):
        """ The background color of the Widget.
        """
        return self._bgcolor

    @bgcolor.setter
    def bgcolor(self, value):
        self._bgcolor = Color(value)
        self._update_colors()
        self._update_line()
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
        self._update_child_widgets()

    def _update_line(self):
        """ Update border line to match new shape """
        w = 1  # XXX Eventually this can be a parameter
        m = int(self.margin)
        # border is drawn within the boundaries of the widget:
        #
        #  size = (8, 7)  margin=2
        #  internal rect = (3, 3, 2, 1)
        #  ........
        #  ........
        #  ..BBBB..
        #  ..B  B..
        #  ..BBBB..
        #  ........
        #  ........
        #
        l = b = m
        r = int(self.size[0]) - m
        t = int(self.size[1]) - m
        pos = np.array([
            [l, b], [l+w, b+w],
            [r, b], [r-w, b+w],
            [r, t], [r-w, t-w],
            [l, t], [l+w, t-w],
        ], dtype=np.float32)
        faces = np.array([
            [0, 2, 1],
            [1, 2, 3],
            [2, 4, 3],
            [3, 5, 4],
            [4, 5, 6],
            [5, 7, 6],
            [6, 0, 7],
            [7, 0, 1],
            [5, 3, 1],
            [1, 5, 7],
        ], dtype=np.int32)
        start = 8 if self._border_color.is_blank else 0
        stop = 8 if self._bgcolor.is_blank else 10
        face_colors = None
        if self._face_colors is not None:
            face_colors = self._face_colors[start:stop]
        self._visual.set_data(vertices=pos, faces=faces[start:stop],
                              face_colors=face_colors)

    def _update_colors(self):
        self._face_colors = np.concatenate(
            (np.tile(self.border_color.rgba, (8, 1)),
             np.tile(self.bgcolor.rgba, (2, 1)))).astype(np.float32)

    def draw(self, event):
        """Draw the widget borders

        Parameters
        ----------
        event : instance of Event
            The event containing the transforms.
        """
        if self.border_color.is_blank and self.bgcolor.is_blank:
            return
        self._visual.draw(event)

    def on_resize(self, event):
        """On resize handler

        Parameters
        ----------
        event : instance of Event
            The resize event.
        """
        self._update_child_widgets()

    def _update_child_widgets(self):
        # Set the position and size of child boxes (only those added
        # using add_widget)
        for ch in self._widgets:
            ch.rect = self.rect.padded(self.padding + self.margin)

    def add_widget(self, widget):
        """
        Add a Widget as a managed child of this Widget.

        The child will be
        automatically positioned and sized to fill the entire space inside
        this Widget (unless _update_child_widgets is redefined).

        Parameters
        ----------
        widget : instance of Widget
            The widget to add.

        Returns
        -------
        widget : instance of Widget
            The widget.
        """
        self._widgets.append(widget)
        widget.parent = self
        self._update_child_widgets()
        return widget

    def add_grid(self, *args, **kwargs):
        """
        Create a new Grid and add it as a child widget.

        All arguments are given to Grid().
        """
        from .grid import Grid
        grid = Grid(*args, **kwargs)
        return self.add_widget(grid)

    def add_view(self, *args, **kwargs):
        """
        Create a new ViewBox and add it as a child widget.

        All arguments are given to ViewBox().
        """
        from .viewbox import ViewBox
        view = ViewBox(*args, **kwargs)
        return self.add_widget(view)

    def remove_widget(self, widget):
        """
        Remove a Widget as a managed child of this Widget.

        Parameters
        ----------
        widget : instance of Widget
            The widget to remove.
        """
        self._widgets.remove(widget)
        widget.remove_parent(self)
        self._update_child_widgets()
