# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
This module provides functions for displaying data from a command-line
interface.

**NOTE**: This module is still experimental, and under development.
It currently lacks axes, but that is a high-priority target for
the next release.

Usage
-----
To use `vispy.plot` typically the main class `Fig` is first instantiated::

    >>> from vispy.plot import Fig
    >>> fig = Fig()

And then `PlotWidget` instances are automatically created by accessing
the ``fig`` instance::

    >>> ax_left = fig[0, 0]
    >>> ax_right = fig[0, 1]

Then plots are accomplished via methods of the `PlotWidget` instances::

    >>> import numpy as np
    >>> data = np.random.randn(2, 10)
    >>> ax_left.plot(data)
    >>> ax_right.histogram(data[1])

"""

from .fig import Fig  # noqa
from .plotwidget import PlotWidget  # noqa
from ..scene import *  # noqa
