# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from os import path as op

from ..util import load_data_file

# This is the package data dir, not the dir for config, etc.
DATA_DIR = op.join(op.dirname(__file__), '_data')


def load_iris():
    """Load the iris dataset

    Returns
    -------
    iris : NpzFile
        data['data'] : a (150, 4) NumPy array with the iris' features
        data['group'] : a (150,) NumPy array with the iris' group
    """
    return np.load(load_data_file('iris/iris.npz',
                                  force_download='2014-09-04'))


def load_crate():
    """Load an image of a crate

    Returns
    -------
    crate : array
        256x256x3 crate image.
    """
    return np.load(load_data_file('orig/crate.npz'))['crate']


def load_spatial_filters(packed=True):
    """Load spatial-filters kernel

    Returns
    -------
    kernel : array
        16x1024x4 (packed float in rgba8) or
        16x1024 (unpacked float)
        16 interpolation kernel with length 1024 each.

    names : tuple of strings
        Respective interpolation names, plus "Nearest" which does
        not require a filter but can still be used
    """
    names = ("Bilinear", "Hanning", "Hamming", "Hermite",
             "Kaiser", "Quadric", "Bicubic", "CatRom",
             "Mitchell", "Spline16", "Spline36", "Gaussian",
             "Bessel", "Sinc", "Lanczos", "Blackman", "Nearest")

    def pack_float_to_rgba(value):
        pack = np.zeros(value.shape + (4,))
        vec = [1., 256., 256., 256.]
        for i, v in enumerate(vec):
            value, pack[..., i] = np.modf(value * v)
        return pack

    kernel = np.load(op.join(DATA_DIR, 'spatial-filters.npy'))
    if packed:
        # convert the kernel to a packed representation
        #kernel = np.fromstring(kernel.tostring(),
        #                       np.ubyte).reshape((kernel.shape + (4,)))
        kernel = pack_float_to_rgba(kernel).astype(np.ubyte)

    return kernel, names
