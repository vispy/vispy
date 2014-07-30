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

        if pos is not None or kwds:
            self._generate_vertices(pos=pos, radius=radius,
                                    start_angle=0.,
                                    span_angle=360.,
                                    num_segments=sides)
            self.mesh = Mesh(pos=self._vertices, color=color)
            self.mesh._primitive = gloo.gl.GL_TRIANGLE_FAN
            if border_color:
                self.border = Line(pos=self._vertices[1:], color=border_color)
