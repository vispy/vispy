# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Plot data from a sound file.
"""

import sys
import numpy as np

from vispy import plot as vp

# Plot a logarithmic chirp
fs = 1000.
N = 10000
t = np.arange(N) / float(fs)
f0, f1 = 1., 500.
phase = (t[-1] / np.log(f1 / f0)) * f0 * (pow(f1 / f0, t / t[-1]) - 1.0)
data = np.cos(2 * np.pi * phase)

fig = vp.Fig(show=False, size=(800, 400))
im = fig[0:2, 0].spectrogram(data, clim=(-100, -20))
fig[2, 0].line(t, data)

if __name__ == '__main__':
    fig.show()
    if sys.flags.interactive == 0:
        fig.app.run()
