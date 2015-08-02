# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# vispy: gallery 1
"""
Plot different styles of ColorBar using vispy.plot
"""

from vispy import plot as vp

fig = vp.Fig(size=(800, 400), show=False)
plot = fig[0, 0]

dimensions = [(200, 10), (10, 200), (10, 200)]
# note: "bottom" could also be used, but this would
# conflict with top.
orientations = ["top", "left", "right"]


for i in range(0, len(dimensions)):
    cbar = plot.colorbar(halfdim=dimensions[i],
                         orientation=orientations[i],
                         label=orientations[i],
                         clim=(0, 100),
                         cmap="winter",
                         border_width=1,
                         border_color="#212121")

if __name__ == '__main__':
    fig.show(run=True)
