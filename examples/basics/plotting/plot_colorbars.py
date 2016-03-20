# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Show use of colorbars in plot
"""
import vispy.plot as vp

fig = vp.Fig(size=(600, 500), show=False)
plotwidget = fig[0, 0]

fig.title = "bollu"
plotwidget.plot([(x, x**2) for x in range(0, 100)], title="y = x^2")
plotwidget.colorbar(position="top", cmap="autumn")

if __name__ == '__main__':
    fig.show(run=True)
