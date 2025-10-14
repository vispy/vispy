# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np
from .mesh import MeshVisual


class CandleVisual(MeshVisual):
    """Visual that calculates and displays a candle chart

    Parameters
    ----------
    ohlc : array-like
        Data for candles - columns are: Open, High, Low, Close, optional 
        another two zero columns, if they are not provided they'll be added - 
        if performance is a consideration, pass np.array(ohlc(zero col)(zero col))
    upcolor : array-like
        [0, 1, 0] rgb array for rising candle color (open < close) 
        Green is default
    downcolor : array-like
        [1, 0, 0] rgb array for falling candle color (open > close)
        Red is default
    color : ColorArray 
        ColorArray or color letter for example 'w' for white
    """

    def __init__(self, ohlc, upcolor=[0, 1, 0], downcolor=[1, 0, 0], color='w', width=0.95, shift=0.0):
        if ohlc.shape[1] == 4:
            ohlc = np.append(ohlc, np.zeros((ohlc.shape[0], 2)), axis=1)
        elif ohlc.shape[1] != 6:
            raise ValueError('ohlc must have 4 or 6 columns')
        
        self.ohlc_size = ohlc.shape[0]

        self.rr, self.tris, self.tris_color = None, None, None
        
        if downcolor is None or upcolor is None:
            self.rr, self.tris, self.tris_color = calculate(ohlc, color='w', width=width, shift=shift)
        else:
            self.rr, self.tris, self.tris_color = calculate(ohlc, upcolor, downcolor, width=width, shift=shift)

        MeshVisual.__init__(self, vertices=self.rr, faces=self.tris, face_colors=self.tris_color, color=color)

    def update_data(self, ohlc_partial=None, ohlc=None, upcolor=[0, 1, 0], downcolor=[1, 0, 0], color='w', width=0.95,
                    shift=0.0):
        if ohlc is not None:
            if ohlc.shape[1] == 4:
                ohlc = np.append(ohlc, np.zeros((ohlc.shape[0], 2)), axis=1)
            elif ohlc.shape[1] != 6:
                raise ValueError('ohlc must have 4 or 6 columns')
        
            if downcolor is None or upcolor is None:
                self.rr, self.tris, color = calculate(ohlc, color=color, width=width, shift=shift)
                MeshVisual.set_data(self, vertices=self.rr, faces=self.tris, color=color)
            else:
                self.rr, self.tris, self.tris_color = calculate(ohlc, upcolor, downcolor, width=width, shift=shift)
                MeshVisual.set_data(self, vertices=self.rr, faces=self.tris, face_colors=self.tris_color)

        else:
            if ohlc_partial is not None:
                if ohlc.shape[1] == 4:
                    ohlc = np.append(ohlc, np.zeros((ohlc.shape[0], 2)), axis=1)
                elif ohlc.shape[1] != 6:
                    raise ValueError('ohlc must have 4 or 6 columns')

                if downcolor is None or upcolor is None:
                    vertices, faces, color = calculate(ohlc_partial, upcolor=None, downcolor=None, 
                                                       offset=self.rr.shape[0], color=color, 
                                                       width=width, shift=shift)

                    self.rr = np.append(self.rr, vertices, axis=0)
                    self.tris = np.append(self.tris, faces, axis=0)

                    MeshVisual.set_data(self, self.rr, self.tris, color=color)

                else:
                    vertices, faces, color_faces = calculate(ohlc_partial, upcolor, downcolor, offset=self.rr.shape[0],
                                                             color=color, width=width, shift=shift)

                    self.rr = np.append(self.rr, vertices, axis=0)
                    self.tris = np.append(self.tris, faces, axis=0)
                    self.tris_color = np.append(self.tris_color, color_faces, axis=0)

                    MeshVisual.set_data(self, self.rr, self.tris, face_colors=self.tris_color, color=color)
                

def calculate(ohlc, upcolor=None, downcolor=None, color='w', offset=0, width=0.95, shift=0.0):
    # Performace i5 6600k:

    # 661 µs ± 171 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each) with 500 candles

    # Theory of Operation:
    # The function takes in a numpy array of OHLC data and returns a vispy scene.

    # Candle vertices for x(0) y low = -1 y high = 4 y open = 0 y close = 3, z= 0 because it is a 2D scene.
    #    x    y     z
    # [-0.24  0.   -0.  ]
    # [-0.48  0.   -0.  ]
    # [-0.48  3.    0.  ]
    # [-0.24  3.    0.  ]
    # [ 0.24  3.    0.  ]
    # [ 0.48  3.    0.  ]
    # [ 0.48  0.   -0.  ]
    # [ 0.24  0.   -0.  ]
    # [ 0.24  4.    0.  ]
    # [-0.24  4.    0.  ]
    # [ 0.24 -1.   -0.  ]
    # [-0.24 -1.   -0.  ]

    # y sequence is generated by the following:
    # simplfied:
    # for i in range(len(ohlc)):
    #     if ohlc[i,0] > ohlc[i,3]:
    #         out[i, 0] = ohlc[i,3]
    #         out[i, 1] = ohlc[i,0]
    #         out[i, 2] = ohlc[i,3]
    #     else:
    #         out[i, 0] = ohlc[i,0]
    #         out[i, 1] = ohlc[i,3]
    #         out[i, 2] = ohlc[i,0]
    #     out[i, 3] = ohlc[i,1]
    #     out[i, 4] = ohlc[i,2]
    
    # for example:
    #     [0, 3, 3,0, 4, -1, ...]
    #     the result is repeated with np.repeat(2) to
    #     [ 0  0  3  3  3  3  0  0  4  4 -1 -1, ...] 
    #     which is the desired sequence for y

    # Candle faces for one candle:
    # [ 0  0  1]
    # [ 0  1  2]
    # [ 0  2  3]
    # [ 0  3  3]
    # [ 0  3  4]
    # [ 0  4  5]
    # [ 0  5  6]
    # [ 8  4  3]
    # [ 8  3  9]
    # [10 11  0]
    # [10  0  7]
    # Subsequent candles get each element +12: 

    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [2 2 2]
    # ...
    # [|number of candles|-1 |number of candles|-1 |number of candles|-1]   (every 12 elements +1)

    y_position = np.zeros((ohlc.shape[0], 6))  # y_position is a numpy array of shape (number of candles, 6)
    down = ohlc.copy()  # down is created to deetrmine the color of the candle and bottom of candle since the bottom 
    # could be open or close depending which is lower

    down[:, 5] = np.where(down[:, 0] - down[:, 3] > 0, 0, np.nan)  # if the open is higher than the close, the bottom
    # is the close

    y_position[:, 0] = np.where(np.isnan(down).any(axis=1), down[:, 0], down[:, 3])  # aranging the y column first is 
    # the bottom of the candle

    y_position[:, 1] = np.where(np.isnan(down).any(axis=1), down[:, 3], down[:, 0])  # arranging the y column second 
    # is the top of the candle

    y_position[:, 2] = y_position[:, 1]  # arranging the y column third is the top of the candle a repeat of the second
    # column just for ease of generating the array of we can use the np.repeat(2)

    y_position[:, 3] = y_position[:, 0]  # arranging the y column fours is the bottom of the candle a repeat of the 
    # first column just for ease of generating the array of we can use the np.repeat(2)

    y_position[:, 4] = ohlc[:, 1]  # arranging the y column fives is the open price

    y_position[:, 5] = ohlc[:, 2]  # arranging the y column sixth is the low of the candle

    y_position_flattened = y_position.flatten()  # flatten the array to 1D to stack it in the y column of the vertices

    y_position_bars = np.repeat(y_position_flattened, 2)  # before stacking the y column of the vertices, repeat the
    # array to than stack it in the y column of the vertices

    # just creating a len(ohlc)x3 array like this:
    stack_n_x12 = np.arange(0, ohlc.shape[0], dtype=int) 
    stack_n_x12 = np.expand_dims(stack_n_x12, axis=1)
    stack_n_x12 = np.repeat(stack_n_x12, 1, axis=1)
    stack_n_x12 = np.repeat(stack_n_x12, 12, axis=0)

    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [0 0 0]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [1 1 1]
    # [2 2 2]
    # ...
    # [|number of candles|-1 |number of candles|-1 |number of candles|-1]
    # every 12 elements +1
    color_faces = None

    # managing the colors of the candles
    if downcolor is not None:
        colors = np.zeros((3, ohlc.shape[0]))

        # mapping color to each face of the candle
        colors[0, :] = np.where(np.isnan(down).any(axis=1), upcolor[0], downcolor[0])
        colors[1, :] = np.where(np.isnan(down).any(axis=1), upcolor[1], downcolor[1])
        colors[2, :] = np.where(np.isnan(down).any(axis=1), upcolor[2], downcolor[2])

        color_faces = np.transpose(colors)  # transpose because array was the wrong way round - i found it easier to
        # generate the array this way

        color_faces = color_faces.repeat(12, axis=0)  # repeat the array for the 12 faces of the candle

    vertices = np.array([[-width / 4 + shift, 0, 0],  # candle vertices 
                        [-width / 2 + shift, 0, 0],
                        [-width / 2 + shift, 0, 0],
                        [-width / 4 + shift, 0, 0],
                        [width / 4 + shift, 0, 0],
                        [width / 2 + shift, 0, 0],
                        [width / 2 + shift, 0, 0],
                        [width / 4 + shift, 0, 0],
                        [width / 4 + shift, 0, 0],
                        [-width / 4 + shift, 0, 0],
                        [width / 4 + shift, 0, 0],
                        [-width / 4 + shift, 0, 0]])

    vertices = np.tile(vertices, (ohlc.shape[0], 1))  # vertices is stacked vertically for each candle

    base_faces = np.array([[0, 0, 1],
                           [0, 1, 2],
                           [0, 2, 3],
                           [0, 3, 3],
                           [0, 3, 4],
                           [0, 4, 5],
                           [0, 5, 6],
                           [0, 6, 7],
                           [8, 4, 3],
                           [8, 3, 9],
                           [10, 11, 0],
                           [10, 0, 7]])

    base_faces = np.tile(base_faces, (ohlc.shape[0], 1))  # base_faces is stacked vertically for each candle

    faces = None

    if offset != 0:
        offset_array = np.ones((stack_n_x12.shape)) * offset/12
        vertices[:, 0] = vertices[:, 0] + (offset_array + stack_n_x12)[:, 0]  # adding the x_position to the vertices 
        # first column

        faces = ((stack_n_x12 + offset_array) * 12 + base_faces).astype(int)  # reusing the stack_n_x12 array to add to
        # the base_faces to the faces array

    else:
        vertices[:, 0] = vertices[:, 0] + stack_n_x12[:, 0]
        faces = stack_n_x12 * 12 + base_faces
    vertices[:, 1] = vertices[:, 1] + y_position_bars  # adding the y_position to the vertices second column

    # vertices are finished

    if color_faces is not None:
        return vertices, faces, color_faces
    else:
        return vertices, faces, color
