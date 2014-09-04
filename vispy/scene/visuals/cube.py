# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np

from ...geometry import create_cube
from ...gloo import set_state, set_depth_mask, set_polygon_offset
from .mesh import Mesh

class Cube(Mesh):
    def __init__(self, vertex_colors=None, **kwds):
        vertices, filled_faces, outline_faces = create_cube()
        outline = True

        Mesh.__init__(self, vertices['position'], filled_faces, vertex_colors)
        if outline:
            self._outline = Mesh(vertices['position'], outline_faces, color = 'black', mode = 'lines')
        else:
            self._outline = None

    def draw(self, event):
        Mesh.draw(self, event)
        if self._outline:
            set_state(polygon_offset=(1, 1), polygon_offset_fill=True)
            self._outline.draw(event)
