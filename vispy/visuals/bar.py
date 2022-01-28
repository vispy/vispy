# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import time
import numpy as np
from datetime import date

from .mesh import MeshVisual


class BarVisual(MeshVisual):
    """Visual that calculates and displays a bar graph

    Parameters
    ----------
    index : array-like
        Index of bar
    bottom : int | float | array-like
        Bottom of the bars
    height : int | float | array-like
        Height of the bars
    width : int | float
        Width of all bars
    color : instance of Color
        Color of the histogram.
    """

    def __init__(self, color='w', index=None, bottom=None, height=None, width=0.8):
        X, Y = (0, 1)

        # construct our vertices
        rr = np.zeros((6 * len(index), 3), np.float32)
        rr[:, X] = np.repeat(index, 6)
        rr[0::6, X] += (1 - width) / 2
        rr[1::6, X] += (1 - width) / 2
        rr[2::6, X] += 1 - (1 - width) / 2
        rr[3::6, X] += (1 - width) / 2
        rr[4::6, X] += 1 - (1 - width) / 2
        rr[5::6, X] += 1 - (1 - width) / 2
        rr[:, Y] = np.repeat(bottom, 6)
        rr[::2, Y] += np.repeat(height, 3)
        index.astype(np.float32)

        MeshVisual.__init__(self, rr, color=color)

    def update_data(self, index=None, bottom=None, height=None, width=None):
        X, Y = (0, 1)
        rr = np.zeros((6 * len(index), 3), np.float32)
        rr[:, X] = np.repeat(index, 6)
        rr[0::6, X] += (1 - width) / 2
        rr[1::6, X] += (1 - width) / 2
        rr[2::6, X] += 1 - (1 - width) / 2
        rr[3::6, X] += (1 - width) / 2
        rr[4::6, X] += 1 - (1 - width) / 2
        rr[5::6, X] += 1 - (1 - width) / 2
        rr[:, Y] = np.repeat(bottom, 6)
        rr[::2, Y] += np.repeat(height, 3)
        index.astype(np.float32)
        MeshVisual.set_data(self, vertices=rr)
