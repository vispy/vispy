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


def load_spatial_filters():
    """Load spatial-filters kernel

    Returns
    -------
    kernel : array
        16x1024 16 interpolation kernel with length 1024 each.
    """
    return np.load(op.join(DATA_DIR, 'spatial-filters.npy'))
