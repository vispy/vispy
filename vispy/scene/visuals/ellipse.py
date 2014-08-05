# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
Simple ellipse visual based on PolygonVisual
"""

from __future__ import division

import numpy as np
from ... import gloo
from .polygon import Polygon, Mesh, Line


class Ellipse(Polygon):
    """
Displays a 2D ellipse
pos = center of ellipse
rad = (xradius, yradius)
default: (1,1)
"""
    def __init__(self, pos=None, color=(0, 0, 0, 0), border_color=None,
                 radius=(0.1, 0.1), start_angle=0., span_angle=360.,
                 num_segments=100, **kwds):
        super(Ellipse, self).__init__()
        self._vertices = None
        self._pos = pos
        self._color = color
        self._border_color = border_color
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
        self._vertices = np.empty([curve_segments+2, 3], dtype=np.float32)
        self._vertices[0] = np.float32([pos[0], pos[1], 0.])
        theta = np.linspace(start_angle, start_angle + (span_angle/180.)*np.pi,
                            curve_segments+1)
        self._vertices[1:, 0] = pos[0] + xr * np.cos(theta)
        self._vertices[1:, 1] = pos[1] + yr * np.sin(theta)
        self._vertices[1:, 2] = 0

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
        if num_segments >= 1:
            self._num_segments = num_segments
            self._update()
    
    def _update(self):
        if self._pos is not None:
            self._generate_vertices(pos=self._pos, radius=self._radius,
                                    start_angle=self._start_angle,
                                    span_angle=self._span_angle,
                                    num_segments=self._num_segments)
            self.mesh = Mesh(pos=self._vertices, color=self._color)
            self.mesh._primitive = gloo.gl.GL_TRIANGLE_FAN
            if self._border_color:
                self.border = Line(pos=self._vertices[1:],
                                   color=self._border_color)
        #self.update()
