# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np
from .mesh import MeshVisual


class BarVisual(MeshVisual):
    """Visual that calculates and displays a bar graph

    Parameters
    ----------
    data : array-like
        1st column is the index, 2nd column is the height, optional 3rd column is bottom
    index : array-like
        Index of bar
    bottom : int | float | array-like
        Bottom of the bars
    height : int | float | array-like
        Height of the bars
    width : int | float
        Width of all bars
    color : instance of Color
        Color of the bar.
    """

    def __init__(self, color='w', data=None, index=None, bottom=None, height=None, width=0.8):
        if (index is None or height is None) and data is None:
            raise ValueError("Either supply the data parameter or supply index AND height")

        if data is not None:
            if data.shape[1] == 2:
                index = data[:, 0]
                height = data[:, 1]
            elif data.shape[1] == 3:
                index = data[:, 0]
                height = data[:, 1]
                bottom = data[:, 2]
            else:
                raise ValueError("expected either 2 or 3 columns not " + data.shape[1] + "columns data array should "
                                                                                         "be arranged as follows: 1st "
                                                                                         "column is the index, "
                                                                                         "2nd column is the height, "
                                                                                         "optional 3rd column is "
                                                                                         "bottom")

        if len(index) != len(height):
            raise ValueError("Index length is not equal to the length of height, which needs to be the same")

        if bottom is not None:
            if len(index) != len(bottom):
                raise ValueError("Index length is not equal to the length of height, which needs to be the same")

        if bottom is None:
            bottom = np.zeros(len(index))

        # construct our vertices

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

        MeshVisual.__init__(self, rr, color=color)

    def update_data(self, data=None, index=None, bottom=None, height=None, width=0.8):
        if (index is None or height is None) and data is None:
            raise ValueError("Either supply the data parameter or supply index AND height")

        if data is not None:
            if data.shape[1] == 2:
                index = data[:, 0]
                height = data[:, 1]
            elif data.shape[1] == 3:
                index = data[:, 0]
                height = data[:, 1]
                bottom = data[:, 2]
            else:
                raise ValueError("expected either 2 or 3 columns not " + data.shape[1] + "columns data array should "
                                                                                         "be arranged as follows: 1st "
                                                                                         "column is the index, "
                                                                                         "2nd column is the height, "
                                                                                         "optional 3rd column is "
                                                                                         "bottom")

        if len(index) != len(height):
            raise ValueError("Index length is not equal to the length of height, which needs to be the same")

        if bottom is not None:
            if len(index) != len(bottom):
                raise ValueError("Index length is not equal to the length of height, which needs to be the same")

        if bottom is None:
            bottom = np.zeros(len(index))

        # construct our vertices

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
