# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
Simple ellipse visual based on PolygonVisual
"""

from __future__ import division

import numpy as np
from ...color import Color
from .polygon import Polygon, Mesh, Line


class Ellipse(Polygon):
    """
    Displays a 2D ellipse

    Parameters
    ----------
    pos : array
        Center of the ellipse
    radius : float | tuple
        Radius or radii of the ellipse
        Defaults to  (0.1, 0.1)
    start_angle : float
        Start angle of the ellipse in degrees
        Defaults to 0.
    span_angle : float
        Span angle of the ellipse in degrees
        Defaults to 0.
    num_segments : int
        Number of segments to be used to draw the ellipse
        Defaults to 100
    """
    def __init__(self, pos=None, color='black', border_color=None,
                 radius=(0.1, 0.1), start_angle=0., span_angle=360.,
                 num_segments=100, **kwds):
        super(Ellipse, self).__init__()
        self._vertices = None
        self._pos = pos
        self._color = Color(color)
        self._border_color = Color(border_color)
        self._radius = radius
        self._start_angle = start_angle
        self._span_angle = span_angle
        self._num_segments = num_segments
        self._update()

    def _generate_vertices(self, pos, radius, start_angle, span_angle,
                           num_segments):
        if isinstance(radius, (list, tuple)):
            if len(radius) == 2:
                xr, yr = radius
            else:
                raise ValueError("radius must be float or 2 value tuple/list"
                                 " (got %s of length %d)" % (type(radius),
                                                             len(radius)))
        else:
            xr = yr = radius
        curve_segments = int(num_segments * span_angle / 360.)
        start_angle *= (np.pi/180.)
        self._vertices = np.empty([curve_segments+2, 2], dtype=np.float32)
        self._vertices[0] = np.float32([pos[0], pos[1]])
        theta = np.linspace(start_angle, start_angle + (span_angle/180.)*np.pi,
                            curve_segments+1)
        self._vertices[1:, 0] = pos[0] + xr * np.cos(theta)
        self._vertices[1:, 1] = pos[1] + yr * np.sin(theta)

    @property
    def radius(self):
        """ The start radii of the ellipse.
        """
        return self._radius

    @radius.setter
    def radius(self, radius):
        self._radius = radius
        self._update()

    @property
    def start_angle(self):
        """ The start start_angle of the ellipse.
        """
        return self._start_angle

    @start_angle.setter
    def start_angle(self, start_angle):
        self._start_angle = start_angle
        self._update()

    @property
    def span_angle(self):
        """ The angular span of the ellipse.
        """
        return self._span_angle

    @span_angle.setter
    def span_angle(self, span_angle):
        self._span_angle = span_angle
        self._update()

    @property
    def num_segments(self):
        """ The number of segments in the ellipse.
        """
        return self._num_segments

    @num_segments.setter
    def num_segments(self, num_segments):
        if num_segments < 1:
            raise ValueError('Ellipse must consist of more than 1 segment')
        self._num_segments = num_segments
        self._update()

    def _update(self):
        if self._pos is not None:
            self._generate_vertices(pos=self._pos, radius=self._radius,
                                    start_angle=self._start_angle,
                                    span_angle=self._span_angle,
                                    num_segments=self._num_segments)
            self.mesh = Mesh(vertices=self._vertices, color=self._color.rgba,
                             mode='triangle_fan')
            if not self._border_color.is_blank():
                self.border = Line(pos=self._vertices[1:],
                                   color=self._border_color.rgba)
        #self.update()
