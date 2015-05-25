# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np


def gaussian_filter(data, sigma):
    """
    Drop-in replacement for scipy.ndimage.gaussian_filter.

    (note: results are only approximately equal to the output of
     gaussian_filter)
    """
    if np.isscalar(sigma):
        sigma = (sigma,) * data.ndim

    baseline = data.mean()
    filtered = data - baseline
    for ax in range(data.ndim):
        s = float(sigma[ax])
        if s == 0:
            continue

        # generate 1D gaussian kernel
        ksize = int(s * 6)
        x = np.arange(-ksize, ksize)
        kernel = np.exp(-x**2 / (2*s**2))
        kshape = [1, ] * data.ndim
        kshape[ax] = len(kernel)
        kernel = kernel.reshape(kshape)

        # convolve as product of FFTs
        shape = data.shape[ax] + ksize
        scale = 1.0 / (abs(s) * (2*np.pi)**0.5)
        filtered = scale * np.fft.irfft(np.fft.rfft(filtered, shape, axis=ax) *
                                        np.fft.rfft(kernel, shape, axis=ax),
                                        axis=ax)

        # clip off extra data
        sl = [slice(None)] * data.ndim
        sl[ax] = slice(filtered.shape[ax]-data.shape[ax], None, None)
        filtered = filtered[sl]
    return filtered + baseline
