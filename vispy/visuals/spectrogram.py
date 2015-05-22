# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np

from .image import ImageVisual
from ..util.fourier import stft, fft_freqs
from ..ext.six import string_types


class SpectrogramVisual(ImageVisual):
    """Calculate and show a spectrogram

    Parameters
    ----------
    x : array-like
        1D signal to operate on. ``If len(x) < n_fft``, x will be
        zero-padded to length ``n_fft``.
    n_fft : int
        Number of FFT points. Much faster for powers of two.
    step : int | None
        Step size between calculations. If None, ``n_fft // 2``
        will be used.
    fs : float
        The sample rate of the data.
    window : str | None
        Window function to use. Can be ``'hann'`` for Hann window, or None
        for no windowing.
    color_scale : {'linear', 'log'}
        Scale to apply to the result of the STFT.
        ``'log'`` will use ``10 * log10(power)``.
    cmap : str
        Colormap name.
    clim : str | tuple
        Colormap limits. Should be ``'auto'`` or a two-element tuple of
        min and max values.
    """
    def __init__(self, x, n_fft=256, step=None, fs=1., window='hann',
                 color_scale='log', cmap='cubehelix', clim='auto'):
        self._n_fft = int(n_fft)
        self._fs = float(fs)
        if not isinstance(color_scale, string_types) or \
                color_scale not in ('log', 'linear'):
            raise ValueError('color_scale must be "linear" or "log"')
        data = stft(x, self._n_fft, step, self._fs, window)
        data = np.abs(data)
        data = 20 * np.log10(data) if color_scale == 'log' else data
        super(SpectrogramVisual, self).__init__(data, clim=clim, cmap=cmap)

    @property
    def freqs(self):
        """The spectrogram frequencies"""
        return fft_freqs(self._n_fft, self._fs)
