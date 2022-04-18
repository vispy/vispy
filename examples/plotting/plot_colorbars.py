# -*- coding: utf-8 -*-
# vispy: gallery 2
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Line plot and colorbar
======================

"""
import vispy.plot as vp

fig = vp.Fig(size=(600, 500), show=False)
plotwidget = fig[0, 0]

fig.title = "bollu"
plotwidget.plot([(x, x**2) for x in range(0, 100)], title="y = x^2")
plotwidget.colorbar(position="top", cmap="autumn")

if __name__ == '__main__':
    fig.show(run=True)
