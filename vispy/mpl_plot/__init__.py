# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Matplotlib plotting backend wrapper.

This module enables converting matplotlib plotting commands to
vispy plotting commands. Support is experimental and incomplete,
proceed with caution.
"""

__all__ = ['show']

try:
    from matplotlib.pyplot import *  # noqa
except ImportError:
    def show():
        raise ImportError('matplotlib could not be found')
else:
    from ._mpl_to_vispy import show  # noqa
