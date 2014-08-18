# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np

from ..util import get_data_file


def load_iris():
    """Load the iris dataset

    Returns
    -------
    iris : NpzFile
        data['data'] : a (150, 4) NumPy array with the iris' features
        data['group'] : a (150,) NumPy array with the iris' group
    """
    return np.load(get_data_file('iris/iris.npz'))
