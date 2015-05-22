# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
RegularPolygonVisual visual based on EllipseVisual
"""

from __future__ import division

from ..color import Color
from .ellipse import EllipseVisual


class RegularPolygonVisual(EllipseVisual):
    """
    Displays a regular polygon

    Parameters
    ----------

    pos : array
        Center of the regular polygon
    color : str | tuple | list of colors
        Fill color of the polygon
    border_color : str | tuple | list of colors
        Border color of the polygon
    radius : float
        Radius of the regular polygon
        Defaults to  0.1
    sides : int
        Number of sides of the regular polygon
    """
    def __init__(self, pos=None, color='black', border_color=None,
                 radius=0.1, sides=4, **kwargs):
        super(EllipseVisual, self).__init__()
        self.mesh.mode = 'triangle_fan'
        self._pos = pos
        self._color = Color(color)
        self._border_color = Color(border_color)
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
        if sides < 3:
            raise ValueError('PolygonVisual must have at least 3 sides, not %s'
                             % sides)
        self._sides = sides
        self._update()

    def _update(self):
        if self._pos is None:
            return
        self._generate_vertices(pos=self._pos, radius=self._radius,
                                start_angle=0.,
                                span_angle=360.,
                                num_segments=self._sides)
        
        if not self._color.is_blank:
            self.mesh.set_data(vertices=self._vertices, 
                               color=self._color.rgba)
        if not self._border_color.is_blank:
            self.border.set_data(pos=self._vertices[1:],
                                 color=self._border_color.rgba)

        self.update()
