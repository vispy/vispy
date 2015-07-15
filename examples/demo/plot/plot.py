# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Plot data with different styles
"""

import numpy as np

from vispy import plot as vp
from vispy.io import load_data_file

data = np.load(load_data_file('electrophys/iv_curve.npz'))['arr_0']
time = np.arange(0, data.shape[1], 1e-4)

fig = vp.Fig(size=(800, 800), show=False)

x = np.linspace(0, 10, 20)
y = np.cos(x)
line = fig[0, 0].plot((x, y), symbol='o', width=3, title='I/V Curve',
                      xlabel='Current (pA)', ylabel='Membrane Potential (mV)')
grid = vp.visuals.GridLines(color=(0, 0, 0, 0.5))
grid.set_gl_state('translucent')
fig[0, 0].view.add(grid)


if __name__ == '__main__':
    fig.show(run=True)
