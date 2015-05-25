# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from ..visuals import VisualNode
from ...visuals import CompoundVisual
from ...visuals.mesh import MeshVisual
from ...visuals.transforms import STTransform
from ...util.event import Event
from ...geometry import Rect
from ...color import Color


class Widget(VisualNode, CompoundVisual):
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
    clip : bool
        Not used :)
    padding : int
        The amount of padding in the widget (i.e. the space reserved between
        the contents and the border).
    margin : int
        The margin to keep outside the widget's border.
    
    """

    def __init__(self, pos=(0, 0), size=(10, 10), border_color=(0, 0, 0, 0),
                 clip=False, padding=0, margin=0, **kwargs):
        # For drawing border. 
        # A mesh is required because GL lines cannot be drawn with predictable
        # shape across all platforms.
        self._mesh = MeshVisual(color=border_color, mode='triangle_strip')
        
        # whether this widget should clip its children
        # (todo)
        self._clip = clip
        
        # reserved space inside border
        self._padding = padding
        
        # reserved space outside border
        self._margin = margin
        
        self._size = 16, 16
        # todo: TTransform (translate only for widgets)

        self._widgets = []
        
        CompoundVisual.__init__(self, [self._mesh])
        VisualNode.__init__(self, **kwargs)
 
        self.transform = STTransform()
        self.events.add(resize=Event)
        self.border_color = border_color
        self.pos = pos
        self.size = size
        self._update_line()
        
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
        return self._mesh.color

    @border_color.setter
    def border_color(self, b):
        b = Color(b)
        self._mesh.set_data(color=b)
        self.update()

    @property
    def bgcolor(self):
        """ The background color of the Widget.
        """
        return self._bgcolor

    @bgcolor.setter
    def bgcolor(self, value):
        self._bgcolor = Color(value)
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
        if self.border_color.is_blank:
            return
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
        r = int(self.size[0]) - m
        t = int(self.size[1]) - m
        
        pos = np.array([
            [m, m], [m+1, m+1],
            [r, m], [r-1, m+1],
            [r, t], [r-1, t-1],
            [m, t], [m+1, t-1],
            [m, m], [m+1, m+1]
        ], dtype=np.float32)
        
        self._mesh.set_data(vertices=pos)

    def on_resize(self, ev):
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

    def add_grid(self, *args, **kwargs):
        """
        Create a new Grid and add it as a child widget.

        All arguments are given to add_widget().
        """
        from .grid import Grid
        grid = Grid()
        return self.add_widget(grid, *args, **kwargs)

    def add_view(self, *args, **kwargs):
        """
        Create a new ViewBox and add it as a child widget.

        All arguments are given to add_widget().
        """
        from .viewbox import ViewBox
        view = ViewBox()
        return self.add_widget(view, *args, **kwargs)

    def remove_widget(self, widget):
        self._widgets.remove(widget)
        widget.remove_parent(self)
        self._update_child_widgets()
