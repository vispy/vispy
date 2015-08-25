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


def pack_unit(value):
    """Packs float values between [0,1] into 4 unsigned int8

    Returns
    -------
    pack: array
        packed interpolation kernel
    """
    pack = np.zeros(value.shape + (4,), dtype=np.ubyte)
    for i in range(4):
        value, pack[..., i] = np.modf(value * 256.)
    return pack


def pack_ieee(value):
    """Packs float ieee binary representation into 4 unsigned int8

    Returns
    -------
    pack: array
        packed interpolation kernel
    """
    return np.fromstring(value.tostring(),
                         np.ubyte).reshape((value.shape + (4,)))


def load_spatial_filters(packed=True):
    """Load spatial-filters kernel

    Returns
    -------
    kernel : array
        16x1024x4 (packed float in rgba) or
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

    kernel = np.load(op.join(DATA_DIR, 'spatial-filters.npy'))
    if packed:
        # convert the kernel to a packed representation
        kernel = pack_unit(kernel)

    return kernel, names
