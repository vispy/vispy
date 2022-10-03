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
    shift : int | float
        Shift of all bars along the x-axis
    color : instance of Color
        Color of the bar.
    orientation : {'h', 'v'}
        Orientation of the histogram - 'h' is default
    """

    def __init__(self, height, bottom=None, width=0.8, shift=0.0, color='w', orientation='h'):
        if bottom is None:
            bottom = np.zeros(height.shape[0])
        
        rr, tris = calc_vertices(height, bottom, width, shift, orientation)

        MeshVisual.__init__(self, rr, tris, color=color)

    def update_data(self, height, bottom=None, width=0.8, shift=0.0, color='w'):
        if bottom is None:
            bottom = np.zeros(height.shape[0])
        rr, tris = calc_vertices(height, bottom, width, shift=shift)

        MeshVisual.set_data(self, rr, tris, color=color)


def calc_vertices(height, bottom, width, shift, orientation):

    y_position = np.zeros((height.shape[0], 2))
    
    y_position[:, 0] = height
    y_position[:, 1] = bottom

    y_position = y_position.flatten().repeat(2)

    stack_n_x2 = np.arange(0, height.shape[0], dtype=int) 
    stack_n_x2 = np.expand_dims(stack_n_x2, axis=1)
    stack_n_x2 = np.repeat(stack_n_x2, 1, axis=1)
    stack_n_x2 = np.repeat(stack_n_x2, 2, axis=0)

    vertices = np.array([
        [-width/2 + shift, 1, 0],
        [width/2 + shift, 1, 0],
        [width/2 + shift, 0, 0],
        [-width/2 + shift, 0, 0]])

    vertices = np.tile(vertices, (height.shape[0], 1))

    if orientation == 'h':
        vertices[:, 0] = vertices[:, 0] + stack_n_x2[:, 0].repeat(2)
        vertices[:, 1] = y_position

    elif orientation == 'v':
        vertices[:, 1] = vertices[:, 0] + stack_n_x2[:, 0].repeat(2)
        vertices[:, 0] = y_position
    else:
        raise ValueError('orientation can only be v (vertical) or h (horizontal). You specified: ' + str(orientation))

    base_faces = np.array([[0, 1, 2], [0, 2, 3]])

    base_faces = np.tile(base_faces, (height.shape[0], 1))

    faces = stack_n_x2*4 + base_faces

    return vertices, faces
