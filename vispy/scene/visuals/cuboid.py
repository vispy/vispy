# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np

from ...geometry import create_cube
from ...gloo import set_state, set_depth_mask, set_polygon_offset
from .mesh import Mesh

class Cuboid(Mesh):
    def __init__(self, length=1.0, width=1.0, depth=1.0, vertex_colors=None,
                 face_colors=None, color=(0.5, 0.5, 1, 1), outline=False,
                 **kwds):
        vertices, filled_indices, outline_indices = create_cube()
        vertices['position'][:, 0] *= length
        vertices['position'][:, 1] *= width
        vertices['position'][:, 2] *= depth

        Mesh.__init__(self, vertices['position'], filled_indices,
                      vertex_colors, face_colors, color)
        if outline:
            self._outline = Mesh(vertices['position'], outline_indices,
                                 color='black', mode='lines')
        else:
            self._outline = None

    def draw(self, event):
        Mesh.draw(self, event)
        if self._outline:
            set_state(polygon_offset=(1, 1), polygon_offset_fill=True)
            self._outline.draw(event)
