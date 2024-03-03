# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np
import math

from .mesh import MeshVisual


class CircleVisual(MeshVisual):
    """Visual that calculates and displays a circle using triangle's

    Parameters
    ----------
    corners : int
        Data to histogram. Currently only 1D data is supported.
    radius : int
        Radius of the circle
    color : ColorArray
        ColorArray or color letter for example 'w' for white
    """

    def __init__(self, corners, radius=1, color='w'):

        color_array = None
        if isinstance(color, (np.ndarray, np.generic)):
            if color.shape[0] > 1:
                color_array = []
                for i in range(len(color)):
                    color_array.append(color[i])
                    if i != (len(color) - 1):
                        color_array.append([0, 0, 0])
                color = None

        rr, tris = self._calculate(corners, radius)

        MeshVisual.__init__(self, rr, tris, color=color, face_colors=color_array)

    def update_data(self, corners, radius=1, color='w'):

        color_array = None
        if isinstance(color, (np.ndarray, np.generic)):
            if color.shape[0] > 1:
                color_array = []
                for i in range(len(color)):
                    color_array.append(color[i])
                    if i != (len(color) - 1):
                        color_array.append([0, 0, 0])
                color = None

        rr, tris = self._calculate(corners, radius)

        MeshVisual.set_data(self, rr, tris, color=color, face_colors=color_array)

    def _calculate(self, corners, radius):
        last_angle = 0
        vertices = []
        for i in range(corners + 1):
            if i != 0:
                y = radius * math.cos(last_angle)
                x = radius * math.sin(last_angle)
                vertices.append((x, y))
                vertices.append((0, 0))
                angle = 2 * math.pi * i / corners
                y = radius * math.cos(angle)
                x = radius * math.sin(angle)
                vertices.append((x, y))
                last_angle = angle
        rr = np.array(vertices)

        tris = np.zeros((2 * (corners + 1) - 2, 3), np.uint32)
        offsets = 3 * np.arange(corners, dtype=np.uint32)[:, np.newaxis]
        tri_1 = np.array([0, 2, 1])
        tri_2 = np.array([2, 0, 3])
        tris[::2] = tri_1 + offsets
        tris[1::2] = tri_2 + offsets
        tris = tris[:tris.shape[0] - 1]

        return rr, tris
