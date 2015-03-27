# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Plot data from a sound file.
"""

import sys
import numpy as np

from vispy import plot as vp

# XXX replace with an actual sound file
fs = 44100
N = 10000
t = np.arange(N) / float(fs)
f0, f1 = 10., 10000.
data = np.sin(2 * np.pi * (f0 + (f1 - f0) * t / t[-1]) * t)

fig = vp.Fig(show=False, size=(800, 400))
fig[0:2, 0].spectrogram(data)
fig[2, 0].line(t, data)

if __name__ == '__main__':
    fig.show()
    if sys.flags.interactive == 0:
        fig.app.run()
