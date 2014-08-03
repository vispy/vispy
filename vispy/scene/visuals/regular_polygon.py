# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
RegularPolygon visual based on EllipseVisual
"""

from __future__ import division

from ... import gloo
from .ellipse import Ellipse, Mesh, Line


class RegularPolygon(Ellipse):
    """
    Displays a regular polygon
    pos = center of polygon
    rad = radius
    sides = number of sides
    """
    def __init__(self, pos=None, color=(0, 0, 0, 0), border_color=None,
                 radius=0.1, sides=4, **kwds):
        super(Ellipse, self).__init__()
        self._pos = pos
        self._color = color
        self._border_color = border_color
        self._radius = radius
        self._sides = sides
        self._update()

    @property
    def sides(self):
        """ The number of sides in the regular polygon.
        """
        return self._sides

    @sides.setter
    def sides(self, sides):
        self._sides = sides
        self._update()

    def _update(self):
        if self._pos is not None:
            self._generate_vertices(pos=self._pos, radius=self._radius,
                                    start_angle=0.,
                                    span_angle=360.,
                                    num_segments=self._sides)
            self.mesh = Mesh(pos=self._vertices, color=self._color)
            self.mesh._primitive = gloo.gl.GL_TRIANGLE_FAN
            if self._border_color:
                self.border = Line(pos=self._vertices[1:],
                                   color=self._border_color)
