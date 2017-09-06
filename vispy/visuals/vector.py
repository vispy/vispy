# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from ..geometry import create_arrow
from .mesh import MeshVisual
from .visual import CompoundVisual


class VectorVisual(CompoundVisual):
    """Visual that displays an arrow/vector for 3d purpose

    Parameters
    ----------
    rows : int
        Number of rows.
    cols : int
        Number of columns.
    radius : float
        Base cylinder radius.
    length : float
        Length of the arrow.
    cone_radius : float
        Radius of the cone base.
           If None, then this defaults to 2x the cylinder radius.
    cone_length : float
        Length of the cone.
           If None, then this defaults to 1/3 of the arrow length.
    vertex_colors : ndarray
        Same as for `MeshVisual` class. See `create_cube` for vertex ordering.
    face_colors : ndarray
        Same as for `MeshVisual` class. See `create_cube` for vertex ordering.
    color : Color
        The `Color` to use when drawing the cube faces.
    shading: one of "smooth", "flat" or None (default)
    """
    def __init__(self, rows, cols, radius, length, cone_radius, cone_length, vertex_colors=None, face_colors=None,
                 color=(0.5, 0.5, 1, 1), shading=None, **kwargs):

        mesh = create_arrow(rows, cols, radius, length,
                 cone_radius, cone_length)

        self._mesh = MeshVisual(vertices=mesh.get_vertices(),
                                faces=mesh.get_faces(),
                                vertex_colors=vertex_colors,
                                face_colors=face_colors, color=color, shading=shading)


        CompoundVisual.__init__(self, [self._mesh], **kwargs)
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
