# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from .cuboid import Cuboid


class Cube(Cuboid):
    def __init__(self, length=1.0, vertex_colors=None, face_colors=None,
                 color=(0.5, 0.5, 1, 1), outline=False):
        Cuboid.__init__(self, length, length, length, vertex_colors,
                        face_colors, color, outline)
