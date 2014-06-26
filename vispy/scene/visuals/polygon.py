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
from ...util.geometry import PolygonData


class Polygon(Visual):
    """
    Displays a 2D polygon
    """
    def __init__(self, pos=None, color=(0, 0, 0, 0),
                 border_color=None, **kwds):
        super(Polygon, self).__init__()

        glopts = kwds.pop('gl_options', 'translucent')
        self.set_gl_options(glopts)
        self.mesh = None
        self.border = None
        self.data = PolygonData(vertices=np.array(pos, dtype=np.float32))
        if pos is not None or kwds:
            self.data.triangulate()
            self.mesh = Mesh(pos=self.data.vertices[self.data.faces],
                             color=color)
            if border_color:
                self.border = Line(pos=
                                   self.data.vertices[self.data.convex_hull],
                                   color=border_color, mode='lines')

    @property
    def transform(self):
        """ The transform that maps the local coordinate frame to the
        coordinate frame of the parent.
        """
        return Visual.transform.fget(self)

    @transform.setter
    def transform(self, tr):
        Visual.transform.fset(self, tr)
        self.mesh.transform = tr
        self.border.transform = tr

    def draw(self, event=None):
        if self.mesh:
            gloo.set_state(polygon_offset_fill=True)
            gloo.set_polygon_offset(1, 1)
            self.mesh.draw()
        if self.border:
            self.border.draw()
