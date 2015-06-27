# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from ..geometry import create_cube
from .mesh import MeshVisual
from .visual import CompoundVisual


class CubeVisual(CompoundVisual):
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

        vertices, filled_indices, outline_indices = create_cube()
        vertices['position'] *= size

        self._mesh = MeshVisual(vertices=vertices['position'],
                                faces=filled_indices,
                                vertex_colors=vertex_colors,
                                face_colors=face_colors, color=color)
        if edge_color:
            self._border = MeshVisual(vertices=vertices['position'],
                                      faces=outline_indices,
                                      color=edge_color, mode='lines')
        else:
            self._border = MeshVisual()

        CompoundVisual.__init__(self, [self._mesh, self._border], **kwargs)
        self.mesh.set_gl_state(polygon_offset_fill=True,
                               polygon_offset=(1, 1), depth_test=True)

    @property
    def mesh(self):
        """The vispy.visuals.MeshVisual that used to fill in.
        """
        return self._mesh

    @mesh.setter
    def mesh(self, mesh):
        self._mesh = mesh

    @property
    def border(self):
        """The vispy.visuals.MeshVisual that used to draw the border.
        """
        return self._border

    @border.setter
    def border(self, border):
        self._border = border
