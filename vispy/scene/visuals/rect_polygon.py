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
degree = degree of curvature of corners between (0,1)
"""
    def __init__(self, pos=None, color='black', border_color=None,
                 radius=0., height=1.0, width=1.0, degree=0., **kwds):
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

        num_segments = int(degree * 500.0)

        hw = min(height/4., width/4.)

        bias1 = width / 2. - degree * hw
        bias2 = height / 2. - degree * hw

        xr = degree * hw
        yr = degree * hw

        corner1 = np.empty([num_segments+1, 3], dtype=np.float32)
        corner2 = np.empty([num_segments+1, 3], dtype=np.float32)
        corner3 = np.empty([num_segments+1, 3], dtype=np.float32)
        corner4 = np.empty([num_segments+1, 3], dtype=np.float32)

        start_angle = 0.
        end_angle = np.pi / 2.

        theta = np.linspace(start_angle, end_angle, num_segments+1)

        corner1[:, 0] = pos[0] + bias1 + xr * np.cos(theta)
        corner1[:, 1] = pos[1] - bias2 - yr * np.sin(theta)
        corner1[:, 2] = 0

        theta = np.linspace(end_angle, start_angle, num_segments+1)

        corner2[:, 0] = pos[0] - bias1 - xr * np.cos(theta)
        corner2[:, 1] = pos[1] - bias2 - yr * np.sin(theta)
        corner2[:, 2] = 0

        theta = np.linspace(start_angle, end_angle, num_segments+1)

        corner3[:, 0] = pos[0] - bias1 - xr * np.cos(theta)
        corner3[:, 1] = pos[1] + bias2 + yr * np.sin(theta)
        corner3[:, 2] = 0

        theta = np.linspace(end_angle, start_angle, num_segments+1)

        corner4[:, 0] = pos[0] + bias1 + xr * np.cos(theta)
        corner4[:, 1] = pos[1] + bias2 + yr * np.sin(theta)
        corner4[:, 2] = 0

        output = np.concatenate(([[pos[0], pos[1], 0.], 
                                  [pos[0] + width / 2., pos[1], 0.]],
                                 corner1, [[pos[0], pos[1] - height / 2., 0.]],
                                 corner2, [[pos[0] - width / 2., pos[1], 0.]],
                                 corner3, [[pos[0], pos[1] + height / 2., 0.]],
                                 corner4, [[pos[0] + width / 2., pos[1], 0.]]))

        self._vertices = np.array(output, dtype=np.float32)

    @property
    def degree(self):
        """ The degree of curvature of rounded corners.
        """
        return self._degree

    @degree.setter
    def degree(self, degree):
        self._degree = degree
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
