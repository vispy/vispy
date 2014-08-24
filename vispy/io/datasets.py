# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from os import path as op

from ..util.fetching import load_data_file

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
    return np.load(load_data_file('iris/iris.npz'))


def load_crate():
    """Load an image of a crate

    Returns
    -------
    crate : array
        256x256x3 crate image.
    """
    return np.load(load_data_file('orig/crate.npz'))['crate']
