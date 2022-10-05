# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np

from vispy.color.color_array import ColorArray
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
    shift : int | float
        Shift of all bars along the x-axis
    color : ColorArray | numpy.ndarray | str
        Color of the bars or you can pass a 2d array with rgb values for each individual bar
    orientation : {'h', 'v'}
        Orientation of the bars - 'v' is default 
        'v' : |
        'h' : -
    color_array : array-like
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]] exactly one rgb array for each bar. This would be for 3 Bars 
    """

    def __init__(self, height, bottom=None, width=0.8, shift=0.0, color='w', orientation='v'):
        if bottom is None:
            bottom = np.zeros(height.shape[0])

        if height.shape != bottom.shape:
            raise ValueError("Height and Bottom must be same shape: Height: " + height.shape + " Bottom: "
                             + bottom.shape)

        color_array = None

        if isinstance(color, np.ndarray):
            if len(color.shape) == 2:
                if color.shape[1] == 3:
                    if color.shape[0] > 1 and color.shape[0] != 0:
                        color_array = np.repeat(color, 2, axis=0)
                        color = None
                else:
                    raise ValueError('If you pass an numpy array as color it needs to be rgb i.e. 3 columns')
        elif isinstance(color, ColorArray):
            pass
        elif isinstance(color, str):
            pass
        else:
            raise ValueError("Color has to be either a vispy ColorArray, numpy array or a string for example: 'w'") 
        
        rr, tris = calc_vertices(height, bottom, width, shift, orientation)

        MeshVisual.__init__(self, rr, tris, color=color, face_colors=color_array)

    def update_data(self, height, bottom=None, width=0.8, shift=0.0, color='w', orientation='v', color_array=None):
        if bottom is None:
            bottom = np.zeros(height.shape[0])

        if height.shape != bottom.shape:
            raise ValueError("Height and Bottom must be same shape: Height: " + height.shape + " Bottom: "
                             + bottom.shape)
        
        color_array = None

        if isinstance(color, np.ndarray):
            if len(color.shape) == 2:
                if color.shape[1] == 3:
                    if color.shape[0] > 1 and color.shape[0] != 0:
                        color_array = np.repeat(color, 2, axis=0)
                        color = None
                else:
                    raise ValueError('If you pass an numpy array as color it needs to be rgb i.e. 3 columns')
        elif isinstance(color, ColorArray):
            pass
        elif isinstance(color, str):
            pass
        else:
            raise ValueError("Color has to be either a vispy ColorArray, numpy array or a string for example: 'w'") 

        rr, tris = calc_vertices(height, bottom, width, shift, orientation)
            
        MeshVisual.set_data(self, rr, tris, color=color, face_colors=color_array)


def calc_vertices(height, bottom, width, shift, orientation):

    y_position = np.zeros((height.shape[0], 2))
    
    y_position[:, 0] = height
    y_position[:, 1] = bottom

    y_position = y_position.flatten().repeat(2)

    stack_n_x2 = np.arange(height.shape[0]).repeat(2).reshape(-1, 1)

    vertices = np.array([
        [-width/2 + shift, 1],
        [width/2 + shift, 1],
        [width/2 + shift, 0],
        [-width/2 + shift, 0]])

    vertices = np.tile(vertices, (height.shape[0], 1))

    if orientation == 'v':
        vertices[:, 0] = vertices[:, 0] + stack_n_x2[:, 0].repeat(2)
        vertices[:, 1] = y_position

    elif orientation == 'h':
        vertices[:, 1] = vertices[:, 0] + stack_n_x2[:, 0].repeat(2)
        vertices[:, 0] = y_position
    else:
        raise ValueError('orientation can only be v (vertical) or h (horizontal). You specified: ' + str(orientation))

    base_faces = np.array([[0, 1, 2], [0, 2, 3]])

    base_faces = np.tile(base_faces, (height.shape[0], 1))

    faces = stack_n_x2 * 4 + base_faces

    return vertices, faces
