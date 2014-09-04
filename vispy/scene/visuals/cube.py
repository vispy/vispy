# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from ...geometry import create_cube
from .mesh import Mesh


class Cube(Mesh):
    def __init__(self, **kwds):
        vert, idx = create_cube()[:2]
        Mesh.__init__(self, vert['position'], idx)
