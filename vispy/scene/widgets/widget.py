# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from ..node import Node
from ...visuals.line import LineVisual
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
        Node.__init__(self, **kwargs)
        
        # for drawing border
        self._visual = LineVisual(method='gl')
        self.border_color = border_color
        # whether this widget should clip its children
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
    def border_color(self):
        """ The color of the border.
        """
        return self._visual.color

    @border_color.setter
    def border_color(self, b):
        b = Color(b)
        self._visual.set_data(color=b)
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
        m = self.margin
        # subtract 1 so border is drawn within the boundaries of the widget:
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
        r = self.size[0] - m - 1
        t = self.size[1] - m - 1
        
        # Drawing pixel-perfect lines is a bit tricky. Getting the correct
        # line _position_ and _length_ requires different considerations. 
        # 
        # Line position:
        # Integer values lie exactly on the boundaries between pixels, which 
        # leads to 1-pixel offsets. Different GL implementations will have
        # different offsets, but adding 0.01 should make the pixel location 
        # unambiguous on all systems:
        # 
        #   y = 0.99    1.0    1.01   1.5
        #     0----------------------------
        #      ====== -------
        #     1----------------------------
        #             ------- ====== ======
        #     2----------------------------
        #               ^ 1.0 is ambiguous; depends on GL implementation!
        #  
        # Line length:
        # Integer values lie at the top-left corner of each pixel, so drawing
        # a segment from x=0 to x=3 results in a line 3 pixels long:
        # 
        #    |===|===|===|   |   x2 = 3
        #    |===|===|===|   |   x2 = 3.49
        #    |===|===|===|---|   x2 = 3.5    --> depends on GL implementation!
        #    |===|===|===|===|   x2 = 3.51
        #    |===|===|===|===|   x2 = 4
        #    0   1   2   3   4
        #   
        # To fill that last pixel, we need to extend the length of the line 
        # by at least 0.51 (the extra 0.01 avoids implementation-dependent 
        # ambiguity).
        # 
        
        r += 0.5  # large enough to extend line length, but small enough to 
        t += 0.5  # avoid shifting the line
        pos = np.array([
            [m, m],
            [r, m],
            [r, t],
            [m, t],
            [m, m]]).astype(np.float32)
        # to avoid system-dependent ambiguity about pixel boundaries
        pos += 0.01  
        
        self._visual.set_data(pos=pos)

    def draw(self, event):
        if self.border_color.is_blank:
            return
        self._visual.draw(event)

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
