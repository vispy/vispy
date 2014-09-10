# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Example of simple mesh plotting and manipulation.
"""

import sys
import numpy as np

from vispy.io import load_data_file
import vispy.plot as vp

fname = load_data_file('orig/triceratops.obj.gz')

canvas = vp.mesh(fname=fname, azimuth=-0, elevation=90, distance=2)

vertex_colors = np.random.rand(canvas.mesh.mesh_data.n_vertices, 3) ** 2
canvas.mesh.mesh_data.set_vertex_colors(vertex_colors)

if __name__ == '__main__':
    canvas.show()
    if sys.flags.interactive == 0:
        canvas.app.run()
