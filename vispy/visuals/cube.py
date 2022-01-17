# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import warnings
from .box import BoxVisual


class CubeVisual(BoxVisual):
    """Visual that displays a cube or cuboid

    Parameters
    ----------
    size : float or tuple
        The size of the cuboid. A float gives a cube, whereas tuples may
        specify the size of each axis (x, y, z) independently.
    vertex_colors : ndarray
        Same as for `MeshVisual` class. See `create_cube` for vertex ordering.
    face_colors : ndarray
        Same as for `MeshVisual` class. See `create_cube` for vertex ordering.
    color : Color
        The `Color` to use when drawing the cube faces.
    edge_color : tuple or Color
        The `Color` to use when drawing the cube edges. If `None`, then no
        cube edges are drawn.
    """

    def __init__(self, size=1.0, vertex_colors=None, face_colors=None,
                 color=(0.5, 0.5, 1, 1), edge_color=None, **kwargs):
        warnings.warn("The CubeVisual is deprecated in favor of BoxVisual",
                      DeprecationWarning, stacklevel=2)
        if isinstance(size, tuple):
            width, height, depth = size
        else:
            width = height = depth = size
        BoxVisual.__init__(self, width=width, height=height, depth=depth,
                           vertex_colors=vertex_colors,
                           face_colors=face_colors, color=color,
                           edge_color=edge_color, **kwargs)
