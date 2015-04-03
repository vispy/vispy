# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Example of plotting multiple things using the quick interface.
"""

import numpy as np

from vispy.io import load_data_file
import vispy.plot.q as vpq

# Mesh
fig = vpq.mesh(fname=load_data_file('orig/triceratops.obj.gz'))
fig[0, 0].camera.up = 'y'
fig[0, 0].camera.flip = True, False, False

# Line
fig_2 = vpq.plot([[1, 6, 2, 4, 3, 8, 4, 6, 5, 2]])

# Image
fig_3 = vpq.image(np.random.normal(128, 60, (20, 40)))

# Scatter plot
fig_4 = vpq.plot(np.array([(0, 2), (1, 6), (2, 1), (6, 10)]).T, width=0)

if __name__ == '__main__':
    fig.app.run()
