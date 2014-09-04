# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from ...geometry import create_cube
from ...gloo import set_state
from .mesh import Mesh


class Cube(Mesh):
    def __init__(self, size=1.0, vertex_colors=None,
                 face_colors=None, color=(0.5, 0.5, 1, 1), outline=False):
        vertices, filled_indices, outline_indices = create_cube()
        vertices['position'] *= size

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
