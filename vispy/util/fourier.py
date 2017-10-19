# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np


def stft(x, n_fft=1024, step=512, fs=2*np.pi, window='hann'):
    """Compute the STFT

    Parameters
    ----------
    x : array-like
        1D signal to operate on. ``If len(x) < n_fft``, x will be zero-padded
        to length ``n_fft``.
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

    Returns
    -------
    stft : ndarray
        Spectrogram of the data, shape (n_freqs, n_steps).

    See also
    --------
    fft_freqs
    """
    x = np.asarray(x, float)
    if x.ndim != 1:
        raise ValueError('x must be 1D')
    if window is not None:
        if window not in ('hann',):
            raise ValueError('window must be "hann" or None')
        w = np.hanning(n_fft)
    else:
        w = np.ones(n_fft)
    n_fft = int(n_fft)
    step = max(n_fft // 2, 1) if step is None else int(step)
    fs = float(fs)
    zero_pad = n_fft - len(x)
    if zero_pad > 0:
        x = np.concatenate((x, np.zeros(zero_pad, float)))
    n_freqs = n_fft // 2 + 1
    n_estimates = (len(x) - n_fft) // step + 1
    result = np.empty((n_freqs, n_estimates), np.complex128)
    for ii in range(n_estimates):
        result[:, ii] = np.fft.rfft(w * x[ii * step:ii * step + n_fft]) / n_fft
    return result


def fft_freqs(n_fft, fs):
    """Return frequencies for DFT

    Parameters
    ----------
    n_fft : int
        Number of points in the FFT.
    fs : float
        The sampling rate.
    """
    return np.arange(0, (n_fft // 2 + 1)) / float(n_fft) * float(fs)
