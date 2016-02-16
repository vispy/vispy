# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Show use of colorbars in plot

Run with
python -i ipython-base.py
"""


import vispy
from vispy.plot import *


fig = Fig(size=(600, 500), show=False)
plotwidget = fig[0, 0]

plotwidget.plot([(x, x**2) for x in range(0, 100)])
plotwidget.colorbar(position="top", cmap="viridis")

if __name__ == '__main__':
    fig.show(run=True)
