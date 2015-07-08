# !/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 30

"""
A scatter plot of 2D points with matching histograms.
"""

import numpy as np

import vispy.plot as vp

np.random.seed(2324)
n = 100000
data = np.empty((n, 2))
lasti = 0
for i in range(1, 20):
    nexti = lasti + (n - lasti) // 2
    scale = np.abs(np.random.randn(2)) + 0.1
    scale[1] = scale.mean()
    data[lasti:nexti] = np.random.normal(size=(nexti-lasti, 2),
                                         loc=np.random.randn(2),
                                         scale=scale / i)
    lasti = nexti
data = data[:lasti]


color = (0.3, 0.5, 0.8)
n_bins = 100

fig = vp.Fig(show=False)
fig[0:4, 0:4].plot(data, symbol='o', width=0, face_color=color + (0.02,),
                   edge_color=None, marker_size=4)
fig[4, 0:4].histogram(data[:, 0], bins=n_bins, color=color, orientation='h')
fig[0:4, 4].histogram(data[:, 1], bins=n_bins, color=color, orientation='v')

if __name__ == '__main__':
    fig.show(run=True)
