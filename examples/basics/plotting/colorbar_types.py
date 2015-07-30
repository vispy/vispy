# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# vispy: gallery 1
"""
Plot different styles of ColorBar
"""

import numpy as np
from vispy import plot as vp

fig = vp.Fig(size=(800, 400), show=False)
plot = fig[0, 0]

centers = [(0, 0), (0, 200), (200, 0), (200, 200)]
dimensions = [(50, 10), (50, 10), (5, 50), (5, 50)]
orientations = ["bottom", "top", "left", "right"]


for i in range(0, len(centers)):
    cbar = plot.colorbar(pos=centers[i],
                         halfdim=dimensions[i],
                         orientation=orientations[i],
                         label=orientations[i],
                         clim=(0, 100),
                         cmap="winter",
                         border_width=4,
                         border_color="#212121")

if __name__ == '__main__':
    fig.show(run=True)
