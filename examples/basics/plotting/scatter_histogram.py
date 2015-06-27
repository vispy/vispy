# !/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 30

"""
A scatter plot of 2D points with matching histograms.
"""

import numpy as np

import vispy.plot as vp

n = 100000
data = np.random.randn(n, 2)
color = (0.8, 0.25, 0.)
n_bins = 100

fig = vp.Fig(show=False)
fig[0:4, 0:4].plot(data, symbol='o', width=0, face_color=color + (0.05,),
                   edge_color=None, marker_size=10.)
fig[4, 0:4].histogram(data[:, 0], bins=n_bins, color=color, orientation='h')
fig[0:4, 4].histogram(data[:, 1], bins=n_bins, color=color, orientation='v')

if __name__ == '__main__':
    fig.show(run=True)
