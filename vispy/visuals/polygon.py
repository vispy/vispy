# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
Simple polygon visual based on MeshVisual
"""

from __future__ import division

import numpy as np

from .. import gloo
from .visual import Visual
from .mesh import MeshVisual
from .line import LineVisual
from scipy.spatial import Delaunay


class PolygonVisual(Visual):
    """
    Displays a 2D polygon
    """
    def __init__(self, pos=None, **kwds):
        super(PolygonVisual, self).__init__()
        
        glopts = kwds.pop('gl_options', 'translucent')
        color = kwds.pop('color')
        border_color = kwds.pop('border')
        self.set_gl_options(glopts)
        self._mesh = None
        self._border = None
        if pos is not None or kwds:
            pos = np.array(pos, dtype=np.float32)
            pos2 = np.delete(pos, 2, 1)
            tri = Delaunay(pos2)
            triangles = pos[tri.simplices]
            self._mesh = MeshVisual(pos=triangles, color=color)
        if border_color:
            self._border = LineVisual(pos=pos[tri.convex_hull],
                                      color=border_color)

    def paint(self):
        self._activate_gl_options()
        if self._mesh:
            gloo.set_state(polygon_offset_fill=True)
            gloo.set_polygon_offset(1, 1)
            self._mesh.paint()
        if self._border:
            self._border.paint()
