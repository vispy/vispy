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
        1st column is the height, optional 2nd column is bottom
    height : array-like
        Height of the bars
    bottom : array-like
        Bottom of the bars
    width : int | float
        Width of all bars
    color : instance of Color
        Color of the bar.
    """

    def __init__(self, data=None, height=None, bottom=None, width=0.8, color='w'):
        if data is None and height is None:
            raise ValueError("Either supply the data parameter or supply index AND height")

        index = None

        if bottom is not None and height is not None:
            if isinstance(bottom, np.ndarray) and isinstance(height, np.ndarray):
                if bottom.shape != height.shape:
                    if len(height.shape) == 1:
                        height = height.reshape(height.shape[0], 1)

                    elif len(height.shape) == 2:
                        if height.shape[1] != 1:
                            raise ValueError('height should only have one column')

                    else:
                        raise ValueError('3d is not expected, just 2d')

                    if len(bottom.shape) == 1:
                        bottom = bottom.reshape(bottom.shape[0], 1)

                    elif len(bottom.shape) == 2:
                        if bottom.shape[1] != 1:
                            raise ValueError('bottom should only have one column')

                    else:
                        raise ValueError('3d is not expected, just 2d')

                    if bottom[0] != height[0]:
                        raise ValueError('bottom and height have to have the same length')
            else:
                if len(bottom) != len(height):
                    raise ValueError('bottom and height have to have the same length')
                else:
                    index = np.arange(len(bottom))

        if isinstance(data, np.ndarray):
            if len(data.shape) == 1:
                height = data.reshape(data.shape[0], 1)
                index = np.arange(height.shape[0])
                bottom = np.zeros(height.shape)

            elif len(data.shape) == 2:
                if data.shape[1] == 1:
                    height = data
                    index = np.arange(height.shape[0])
                    bottom = np.zeros(height.shape)

                elif data.shape[1] == 2:
                    tmp_height = data[:, 0]
                    height = tmp_height.reshape(tmp_height.shape[0], 1)
                    index = np.arange(height.shape[0])
                    tmp_bottom = data[:, 1]
                    bottom = tmp_bottom.reshape(tmp_bottom.shape[0], 1)

                else:
                    raise ValueError('data should have one column for height and an optionally a second for bottom of '
                                     'bars')

            else:
                raise ValueError('3d is not expected, just 2d')

        elif height is not None:
            if isinstance(height, np.ndarray):
                if len(height.shape) == 1:
                    height = height.reshape(height.shape[0], 1)
                    index = np.arange(height.shape[0])
                    if bottom is None:
                        bottom = np.zeros(height.shape)

                elif len(height.shape) == 2:
                    if height.shape[1] == 1:
                        index = np.arange(height.shape[0])
                        if bottom is None:
                            bottom = np.zeros(height.shape)

                    else:
                        raise ValueError('height should only have one column')

                else:
                    raise ValueError('3d is not expected, just 2d')
            else:
                index = np.arange(len(height))
        else:
            ValueError("Unknown ValueError: height")

        # construct our vertices

        X, Y = (0, 1)

        rr = np.zeros((6 * len(index), 3), np.float32)
        rr[:, X] = np.repeat(index - 0.5, 6)
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

    def update_data(self, data=None, height=None, bottom=None, width=0.8, color='w'):
        if data is None and height is None:
            raise ValueError("Either supply the data parameter or supply index AND height")

        index = None

        if bottom is not None and height is not None:
            if isinstance(bottom, np.ndarray) and isinstance(height, np.ndarray):
                if bottom.shape != height.shape:
                    if len(height.shape) == 1:
                        height = height.reshape(height.shape[0], 1)

                    elif len(height.shape) == 2:
                        if height.shape[1] != 1:
                            raise ValueError('height should only have one column')

                    else:
                        raise ValueError('3d is not expected, just 2d')

                    if len(bottom.shape) == 1:
                        bottom = bottom.reshape(bottom.shape[0], 1)

                    elif len(bottom.shape) == 2:
                        if bottom.shape[1] != 1:
                            raise ValueError('bottom should only have one column')

                    else:
                        raise ValueError('3d is not expected, just 2d')

                    if bottom[0] != height[0]:
                        raise ValueError('bottom and height have to have the same length')
            else:
                if len(bottom) != len(height):
                    raise ValueError('bottom and height have to have the same length')
                else:
                    index = np.arange(len(bottom))

        if isinstance(data, np.ndarray):
            if len(data.shape) == 1:
                height = data.reshape(data.shape[0], 1)
                index = np.arange(height.shape[0])
                bottom = np.zeros(height.shape)

            elif len(data.shape) == 2:
                if data.shape[1] == 1:
                    height = data
                    index = np.arange(height.shape[0])
                    bottom = np.zeros(height.shape)

                elif data.shape[1] == 2:
                    tmp_height = data[:, 0]
                    height = tmp_height.reshape(tmp_height.shape[0], 1)
                    index = np.arange(height.shape[0])
                    tmp_bottom = data[:, 1]
                    bottom = tmp_bottom.reshape(tmp_bottom.shape[0], 1)

                else:
                    raise ValueError('data should have one column for height and an optionally a second for bottom of '
                                     'bars')

            else:
                raise ValueError('3d is not expected, just 2d')

        elif height is not None:
            if isinstance(height, np.ndarray):
                if len(height.shape) == 1:
                    height = height.reshape(height.shape[0], 1)
                    index = np.arange(height.shape[0])
                    if bottom is None:
                        bottom = np.zeros(height.shape)

                elif len(height.shape) == 2:
                    if height.shape[1] == 1:
                        index = np.arange(height.shape[0])
                        if bottom is None:
                            bottom = np.zeros(height.shape)

                    else:
                        raise ValueError('height should only have one column')

                else:
                    raise ValueError('3d is not expected, just 2d')
            else:
                index = np.arange(len(height))
        else:
            ValueError("Unknown ValueError: height")

        # construct our vertices

        X, Y = (0, 1)
        rr = np.zeros((6 * len(index), 3), np.float32)
        rr[:, X] = np.repeat(index - 0.5, 6)
        rr[0::6, X] += (1 - width) / 2
        rr[1::6, X] += (1 - width) / 2
        rr[2::6, X] += 1 - (1 - width) / 2
        rr[3::6, X] += (1 - width) / 2
        rr[4::6, X] += 1 - (1 - width) / 2
        rr[5::6, X] += 1 - (1 - width) / 2
        rr[:, Y] = np.repeat(bottom, 6)
        rr[::2, Y] += np.repeat(height, 3)
        index.astype(np.float32)
        MeshVisual.set_data(self, vertices=rr, color=color)
