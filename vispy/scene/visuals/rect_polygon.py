# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
Simple ellipse visual based on PolygonVisual
"""

from __future__ import division

import numpy as np
from ... import gloo
from ...color import Color
from .polygon import Polygon, Mesh, Line


class RectPolygon(Polygon):
    """
Displays a 2D rectangle
pos = center of rectangle
height = length of the rectangle along y-axis
width = length of the rectangle along x-axis
radius = radius of curvature of corners
"""
    def __init__(self, pos=None, color='black', border_color=None,
                 radius=0., height=1.0, width=1.0, **kwds):
        super(RectPolygon, self).__init__()
        self._vertices = None
        self._pos = pos
        self._color = Color(color)
        self._border_color = Color(border_color)
        self._degree = degree
        self._height = height
        self._width = width
        self._update()

    def _generate_vertices(self, pos, degree, height, width):
        
        self._vertices = np.array([[pos[0], pos[1], 0.],
                                   [pos[0], pos[1]+height/2., 0.],
                                   [pos[0]+width/2., pos[1], 0.],
                                   [pos[0], pos[1]-height/2., 0.],
                                   [pos[0]-width/2., pos[1], 0.],
                                   [pos[0], pos[1]+height/2., 0.]],
                                   dtype=np.float32)

        num_segments = int(degree * 100.0)
        bias1 = degree * width
        bias2 = degree * height
        """
        corner = np.empty([num_segments+1, 3], dtype=np.float32)
        corner[0] = np.float32([pos[0], pos[1], 0.])
        theta = np.linspace(start_angle, start_angle + (span_angle/180.)*np.pi,
                            curve_segments+1)
        self._vertices[1:, 0] = pos[0] + xr * np.cos(theta)
        self._vertices[1:, 1] = pos[1] + yr * np.sin(theta)
        self._vertices[1:, 2] = 0
        """

    @property
    def degree(self):
        """ The degree of curvature of rounded corners.
        """
        return self._degree

    @degree.setter
    def degree(self, degree):
        self._radius = degree
        self._update()
    
    def _update(self):
        if self._pos is not None:
            self._generate_vertices(pos=self._pos, degree=self._degree,
                                    height=self._height, width=self._width,
                                    )
            self.mesh = Mesh(pos=self._vertices, color=self._color.rgba)
            self.mesh._primitive = gloo.gl.GL_TRIANGLE_FAN
            if not self._border_color.is_blank():
                self.border = Line(pos=self._vertices[1:],
                                   color=self._border_color.rgba)
        #self.update()
