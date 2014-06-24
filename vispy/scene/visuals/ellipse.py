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
from ...util.geometry import PolygonData


class Ellipse(Polygon):
    """
    Displays a 2D ellipse
    pos = center of ellipse
    rad = (xradius, yradius)
        default: (1,1)
    """
    def __init__(self, pos=None, color=(0, 0, 0, 0), border_color=None,
                 radius=(0.1, 0.1), **kwds):
        super(Ellipse, self).__init__()

        glopts = kwds.pop('gl_options', 'translucent')
        self.set_gl_options(glopts)
        self.mesh = None
        self.border = None
        self._vertices = None
        if pos is not None or kwds:
            self._generate_vertices(pos=pos, radius=radius)
            self.data = PolygonData(vertices=self._vertices)
            self.data.triangulate()
            self.mesh = Mesh(pos=self.data.vertices[self.data.faces],
                             color=color)
            if border_color:
                self.border = Line(pos=
                                   self.data.vertices[self.data.convex_hull],
                                   color=border_color, mode='lines')


    def _generate_vertices(self, pos, radius, num_segments=100):
        xr, yr = radius
        n_inverse = 1/num_segments
        self._vertices = np.empty([0, 3], dtype=np.float32)
        for t in range(num_segments):
            theta = t*n_inverse*2*np.pi
            self._vertices = np.append(self._vertices, [np.float32([pos[0]+xr*np.cos(theta), pos[1]+yr*np.sin(theta), 0])], axis=0)
