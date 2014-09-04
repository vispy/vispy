# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np

from ...geometry import create_cube
from ...gloo import set_state
from .mesh import Mesh

#        vert_colors = np.empty((len(vert), 4), dtype = np.float32)
#        vert_colors[:, :3] = (vert['position'] + 1.0) / 2.0
#        vert_colors[:, 3] = 1.0


class Cube(Mesh):
    def __init__(self, outline=True, **kwds):
        vertices, filled_ind, outline_ind = create_cube()

        Mesh.__init__(self, vertices['position'], filled_ind)
        if outline:
            self._outline = Mesh(vertices['position'], outline_ind, color = 'black', mode = 'lines')
        else:
            self._outline = None

    def draw(self, event):
        Mesh.draw(self, event)
        if self._outline:
            self._outline.draw(event)
