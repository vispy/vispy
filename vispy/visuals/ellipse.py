# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
Simple ellipse visual based on PolygonVisual
"""

from __future__ import division

import numpy as np
from .polygon import PolygonVisual


class EllipseVisual(PolygonVisual):
    """
    Displays a 2D ellipse

    Parameters
    ----------
    center : array
        Center of the ellipse
    color : instance of Color
        The face color to use.
    border_color : instance of Color
        The border color to use.
    border_width: float
        The width of the border in pixels
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
    def __init__(self, center=None, color='black', border_color=None,
                 border_width=1, radius=(0.1, 0.1), start_angle=0.,
                 span_angle=360., num_segments=100, **kwargs):
        self._center = center
        self._radius = radius
        self._start_angle = start_angle
        self._span_angle = span_angle
        self._num_segments = num_segments

        PolygonVisual.__init__(self, pos=None, color=color,
                               border_color=border_color,
                               border_width=border_width, **kwargs)

        self._mesh.mode = "triangle_fan"
        self._update()

    @staticmethod
    def _generate_vertices(center, radius, start_angle, span_angle,
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

        start_angle = np.deg2rad(start_angle)

        vertices = np.empty([num_segments + 2, 2], dtype=np.float32)

        # split the total angle into num_segments intances
        theta = np.linspace(start_angle,
                            start_angle + np.deg2rad(span_angle),
                            num_segments + 1)

        # PolarProjection
        vertices[:-1, 0] = center[0] + xr * np.cos(theta)
        vertices[:-1, 1] = center[1] + yr * np.sin(theta)

        # close the curve
        vertices[num_segments + 1] = np.float32([center[0], center[1]])

        return vertices

    @property
    def center(self):
        """ The center of the ellipse
        """
        return self._center

    @center.setter
    def center(self, center):
        """ The center of the ellipse
        """
        self._center = center
        self._update()

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
        num_segments = int(num_segments)
        if num_segments < 1:
            raise ValueError('EllipseVisual must consist of more than 1 '
                             'segment')
        self._num_segments = num_segments
        self._update()

    def _update(self):
        if self._center is None:
            return

        vertices = self._generate_vertices(center=self._center,
                                           radius=self._radius,
                                           start_angle=self._start_angle,
                                           span_angle=self._span_angle,
                                           num_segments=self._num_segments)

        # NOTE: we do not use PolygonVisual's
        # inbuilt update() because the triangulation method
        # it uses is expensive. See discussion on
        # (campagnola/vispy #2) for more details
        if not self._color.is_blank:
            self._mesh.set_data(vertices=vertices,
                                color=self._color.rgba)

        # connect vertices for a closed loop when
        # drawing the border. However, delete the last
        # vertex so there is no line connecting the center
        # to the border
        if not self._border_color.is_blank:
            border_pos = vertices[:-1]

            self._border.set_data(pos=border_pos,
                                  color=self._border_color.rgba,
                                  width=self._border_width,
                                  connect='strip')
