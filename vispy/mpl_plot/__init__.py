# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

try:
    from matplotlib.pyplot import *  # noqa
except ImportError:
    def show():
        raise ImportError('matplotlib could not be found')
else:
    from ._mpl_to_vispy import show  # noqa
