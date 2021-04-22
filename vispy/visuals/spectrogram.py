# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np

from .image import ImageVisual
from ..util.fourier import stft, fft_freqs


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
    normalize : bool
        Normalization of spectrogram values across frequencies.
    color_scale : {'linear', 'log'}
        Scale to apply to the result of the STFT.
        ``'log'`` will use ``10 * log10(power)``.
    cmap : str
        Colormap name.
    clim : str | tuple
        Colormap limits. Should be ``'auto'`` or a two-element tuple of
        min and max values.
    """

    def __init__(self, x=None, n_fft=256, step=None, fs=1., window='hann',
                 normalize=False, color_scale='log', cmap='cubehelix',
                 clim='auto'):
        self._x = np.asarray(x)
        self._n_fft = int(n_fft)
        self._step = step
        self._fs = float(fs)
        self._window = window
        self._normalize = normalize
        self._color_scale = color_scale

        if clim == 'auto':
            self._clim_auto = True
        else:
            self._clim_auto = False

        if not isinstance(self._color_scale, str) or \
                self._color_scale not in ('log', 'linear'):
            raise ValueError('color_scale must be "linear" or "log"')

        data = self._calculate_spectrogram()
        super(SpectrogramVisual, self).__init__(data, clim=clim, cmap=cmap)

    @property
    def freqs(self):
        """The spectrogram frequencies"""
        return fft_freqs(self._n_fft, self._fs)

    @property
    def x(self):
        """The original signal"""
        return self._x

    @x.setter
    def x(self, x):
        self._x = np.asarray(x)
        self._update_image()

    @property
    def n_fft(self):
        """The length of fft window"""
        return self._n_fft

    @n_fft.setter
    def n_fft(self, n_fft):
        self._n_fft = int(n_fft)
        self._update_image()

    @property
    def step(self):
        """The step of fft window"""
        if self._step is None:
            return self._n_fft // 2
        else:
            return self._step

    @step.setter
    def step(self, step):
        self._step = step
        self._update_image()

    @property
    def fs(self):
        """The sampling frequency"""
        return self._fs

    @fs.setter
    def fs(self, fs):
        self._fs = fs
        self._update_image()

    @property
    def window(self):
        """The used window function"""
        return self._window

    @window.setter
    def window(self, window):
        self._window = window
        self._update_image()

    @property
    def color_scale(self):
        """The color scale"""
        return self._color_scale

    @color_scale.setter
    def color_scale(self, color_scale):
        if not isinstance(color_scale, str) or \
                color_scale not in ('log', 'linear'):
            raise ValueError('color_scale must be "linear" or "log"')
        self._color_scale = color_scale
        self._update_image()

    @property
    def normalize(self):
        """The normalization setting"""
        return self._normalize

    @normalize.setter
    def normalize(self, normalize):
        self._normalize = normalize
        self._update_image()

    def _calculate_spectrogram(self):
        if self._x is not None:
            x = self._x
            nan_mean = np.nanmean(x)
            idx = np.isnan(x)
            x[idx] = nan_mean
            data = stft(x, self._n_fft, self._step, self._fs, self._window)
            data = np.abs(data)
            data = 20 * np.log10(data) if self._color_scale == 'log' else data
            if self._normalize:
                for i in range(data.shape[0]):
                    data[i, :] -= np.mean(data[i, :])
                    data[i, :] /= np.std(data[i, :])
            return data.astype(np.float32)  # ImageVisual will warn if 64-bit
        else:
            return None

    def _update_image(self):
        data = self._calculate_spectrogram()
        self.set_data(data)
        self.update()
        if self._clim_auto:
            self.clim = 'auto'
