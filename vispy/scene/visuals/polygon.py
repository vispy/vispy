# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
Simple polygon visual based on MeshVisual and LineVisual
"""

from __future__ import division

import numpy as np

from ... import gloo
from .visual import Visual
from .mesh import Mesh
from .line import Line
from ...color import Color
from ...util.geometry import PolygonData


class Polygon(Visual):
    """
    Displays a 2D polygon
    """
    def __init__(self, pos=None, color='black',
                 border_color=None, **kwds):
        super(Polygon, self).__init__(**kwds)

        self.mesh = None
        self.border = None
        self._pos = pos
        self._color = Color(color)
        self._border_color = Color(border_color)
        self._update()
        #glopts = kwds.pop('gl_options', 'translucent')
        #self.set_gl_options(glopts)

    @property
    def transform(self):
        """ The transform that maps the local coordinate frame to the
        coordinate frame of the parent.
        """
        return Visual.transform.fget(self)

    @transform.setter
    def transform(self, tr):
        Visual.transform.fset(self, tr)
        if self.mesh is not None:
            self.mesh.transform = tr
        if self.border is not None:
            self.border.transform = tr

    @property
    def pos(self):
        """ The vertex position of the polygon.
        """
        return self._pos

    @pos.setter
    def pos(self, pos):
        self._pos = pos
        self._update()

    @property
    def color(self):
        """ The color of the polygon.
        """
        return self._color

    @color.setter
    def color(self, color):
        self._color = Color(color)
        self._update()

    @property
    def border_color(self):
        """ The border color of the polygon.
        """
        return self._border_color

    @border_color.setter
    def border_color(self, border_color):
        self._border_color = Color(border_color)
        self._update()

    def _update(self):
        self.data = PolygonData(vertices=np.array(self._pos, dtype=np.float32))
        if self._pos is not None:
            self.data.triangulate()
            self.mesh = Mesh(pos=self.data.vertices[self.data.faces],
                             color=self._color.rgba)
            if not self._border_color.is_blank():
                border_pos = self.data.vertices[self.data.convex_hull]
                self.border = Line(pos=border_pos,
                                   color=self._border_color.rgba, mode='lines')
        #self.update()

    def set_gl_options(self, *args, **kwds):
        self.mesh.set_gl_options(*args, **kwds)

    def update_gl_options(self, *args, **kwds):
        self.mesh.update_gl_options(*args, **kwds)

    def draw(self, event):
        if self.mesh is not None:
            gloo.set_state(polygon_offset_fill=True)
            gloo.set_polygon_offset(1, 1)
            self.mesh.draw(event)
        if self.border is not None:
            self.border.draw(event)
