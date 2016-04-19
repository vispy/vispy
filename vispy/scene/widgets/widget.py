# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from ..visuals import Compound
from ...visuals.mesh import MeshVisual
from ...visuals.transforms import STTransform
from ...visuals.filters import Clipper
from ...util.event import Event
from ...geometry import Rect
from ...color import Color


class Widget(Compound):
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
    border_width : float
        The width of the border line in pixels.
    bgcolor : color
        The background color.
    padding : int
        The amount of padding in the widget (i.e. the space reserved between
        the contents and the border).
    margin : int
        The margin to keep outside the widget's border.
    """

    def __init__(self, pos=(0, 0), size=(10, 10), border_color=None,
                 border_width=1, bgcolor=None, padding=0, margin=0, **kwargs):
        # For drawing border.
        # A mesh is required because GL lines cannot be drawn with predictable
        # shape across all platforms.
        self._mesh = MeshVisual(color=border_color, mode='triangles')
        self._mesh.set_gl_state('translucent', depth_test=False,
                                cull_face=False)
        self._picking_mesh = MeshVisual(mode='triangle_fan')
        self._picking_mesh.set_gl_state(cull_face=False)
        self._picking_mesh.visible = False

        # reserved space inside border
        self._padding = padding

        self._border_width = border_width

        # reserved space outside border
        self._margin = margin
        self._size = 100, 100

        # layout interaction
        self._width_limits = [0, None]
        self._height_limits = [0, None]
        self._stretch = [None, None]

        # used by the constraint solver
        # in Grid - these are Cassowary variables
        self._var_w = self._var_h = None
        self._var_x = self._var_y = None

        self._widgets = []
        self._border_color = Color(border_color)
        self._bgcolor = Color(bgcolor)
        self._face_colors = None

        Compound.__init__(self, [self._mesh, self._picking_mesh], **kwargs)

        self.transform = STTransform()
        self.events.add(resize=Event)
        self.pos = pos
        self._update_colors()
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

    @property
    def size(self):
        """The size (w, h) of this widget.

        If the widget is a child of another widget, then its size is assigned
        automatically by its parent.
        """
        return self._size

    @size.setter
    def size(self, s):
        assert isinstance(s, tuple)
        assert len(s) == 2
        if self._size == s:
            return
        self._size = s
        self._update_line()
        self._update_child_widgets()
        self._update_clipper()
        self.events.resize()

    @property
    def width(self):
        """The actual width of this widget"""
        return self._size[0]

    @property
    def width_min(self):
        """The minimum width the widget can have"""
        return self._width_limits[0]

    @width_min.setter
    def width_min(self, width_min):
        """Set the minimum height of the widget

        Parameters
        ----------

        height_min: float
            the minimum height of the widget
        """

        if width_min is None:
            self._width_limits[0] = 0
            return

        width_min = float(width_min)
        assert(0 <= width_min)

        self._width_limits[0] = width_min
        self._update_layout()

    @property
    def width_max(self):
        """The maximum width the widget can have"""
        return self._width_limits[1]

    @width_max.setter
    def width_max(self, width_max):
        """Set the maximum width of the widget.

        Parameters
        ----------
        width_max: None | float
            the maximum width of the widget. if None, maximum width
            is unbounded
        """
        if width_max is None:
            self._width_limits[1] = None
            return

        width_max = float(width_max)
        assert(self.width_min <= width_max)

        self._width_limits[1] = width_max
        self._update_layout()

    @property
    def height(self):
        """The actual height of the widget"""
        return self._size[1]

    @property
    def height_min(self):
        """The minimum height of the widget"""
        return self._height_limits[0]

    @height_min.setter
    def height_min(self, height_min):
        """Set the minimum height of the widget

        Parameters
        ----------

        height_min: float
            the minimum height of the widget
        """
        if height_min is None:
            self._height_limits[0] = 0
            return

        height_min = float(height_min)
        assert(height_min >= 0)

        self._height_limits[0] = height_min
        self._update_layout()

    @property
    def height_max(self):
        """The maximum height of the widget"""
        return self._height_limits[1]

    @height_max.setter
    def height_max(self, height_max):
        """Set the maximum height of the widget.

        Parameters
        ----------
        height_max: None | float
            the maximum height of the widget. if None, maximum height
            is unbounded
        """
        if height_max is None:
            self._height_limits[1] = None
            return

        height_max = float(height_max)
        assert(0 <= self.height_min <= height_max)
        self._height_limits[1] = height_max
        self._update_layout()

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
        """The rectangular area inside the margin, border, and padding.

        Generally widgets should avoid drawing or placing sub-widgets outside
        this rectangle.
        """
        m = self.margin + self._border_width + self.padding
        if not self.border_color.is_blank:
            m += 1
        return Rect((m, m), (self.size[0]-2*m, self.size[1]-2*m))

    @property
    def stretch(self):
        """Stretch factors (w, h) used when determining how much space to
        allocate to this widget in a layout.

        If either stretch factor is None, then it will be assigned when the
        widget is added to a layout based on the number of columns or rows it
        occupies.
        """
        return self._stretch

    @stretch.setter
    def stretch(self, s):
        self._stretch = [float(s[0]), float(s[1])]

        if self._stretch[0] == 0:
            raise RuntimeError("received 0 as stretch parameter: %s", s)

        if self._stretch[1] == 0:
            raise RuntimeError("received 0 as stretch parameter: %s", s)

        self._update_layout()

    def _update_layout(self):
        if isinstance(self.parent, Widget):
            self.parent._update_child_widgets()

    def _update_clipper(self):
        """Called whenever the clipper for this widget may need to be updated.
        """
        if self.clip_children and self._clipper is None:
            self._clipper = Clipper()
        elif not self.clip_children:
            self._clipper = None

        if self._clipper is None:
            return
        self._clipper.rect = self.inner_rect
        self._clipper.transform = self.get_transform('framebuffer', 'visual')

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
        self._update_child_widgets()
        self._update_line()
        self.update()
        self.events.resize()

    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, p):
        self._padding = p
        self._update_child_widgets()
        self.update()

    def _update_line(self):
        """ Update border line to match new shape """
        w = self._border_width
        m = self.margin
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
        r = self.size[0] - m
        t = self.size[1] - m
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
        self._mesh.set_data(vertices=pos, faces=faces[start:stop],
                            face_colors=face_colors)

        # picking mesh covers the entire area
        self._picking_mesh.set_data(vertices=pos[::2])

    def _update_colors(self):
        self._face_colors = np.concatenate(
            (np.tile(self.border_color.rgba, (8, 1)),
             np.tile(self.bgcolor.rgba, (2, 1)))).astype(np.float32)
        self._update_visibility()

    @property
    def picking(self):
        return self._picking

    @picking.setter
    def picking(self, p):
        Compound.picking.fset(self, p)
        self._update_visibility()

    def _update_visibility(self):
        blank = self.border_color.is_blank and self.bgcolor.is_blank
        picking = self.picking
        self._picking_mesh.visible = picking and self.interactive
        self._mesh.visible = not picking and not blank

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
        widget.parent = None
        self._update_child_widgets()
