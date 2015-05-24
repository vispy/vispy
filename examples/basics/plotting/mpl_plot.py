# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Example demonstrating how to use vispy.pyplot, which uses mplexporter
to convert matplotlib commands to vispy draw commands.

Requires matplotlib.
"""

import numpy as np

# You can use either matplotlib or vispy to render this example:
# import matplotlib.pyplot as plt
import vispy.mpl_plot as plt

from vispy.io import read_png, load_data_file

n = 200
freq = 10
fs = 100.
t = np.arange(n) / fs
tone = np.sin(2*np.pi*freq*t)
noise = np.random.RandomState(0).randn(n)
signal = tone + noise
magnitude = np.abs(np.fft.fft(signal))
freqs = np.fft.fftfreq(n, 1. / fs)
flim = n // 2

# Signal
fig = plt.figure()
ax = plt.subplot(311)
ax.imshow(read_png(load_data_file('pyplot/logo.png')))

ax = plt.subplot(312)
ax.plot(t, signal, 'k-')

# Frequency content
ax = plt.subplot(313)
idx = np.argmax(magnitude[:flim])
ax.text(freqs[idx], magnitude[idx], 'Max: %s Hz' % freqs[idx],
        verticalalignment='top')
ax.plot(freqs[:flim], magnitude[:flim], 'k-o')

plt.draw()

# NOTE: show() has currently been overwritten to convert to vispy format, so:
# 1. It must be called to show the results, and
# 2. Any plotting commands executed after this will not take effect.
# We are working to remove this limitation.

if __name__ == '__main__':
    plt.show(True)
