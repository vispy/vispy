# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from ..geometry import create_sphere
from ..gloo import set_state
from .mesh import MeshVisual


class SphereVisual(MeshVisual):
    """Visual that displays a sphere

    Parameters
    ----------
    radius : float
        The size of the sphere.
    cols, rows : int
        Number of rows and cols that make up the sphere mesh.
    vertex_colors : ndarray
        Same as for `MeshVisual` class. See `create_sphere` for vertex ordering.
    face_colors : ndarray
        Same as for `MeshVisual` class. See `create_sphere` for vertex ordering.
    color : Color
        The `Color` to use when drawing the sphere faces.
    edge_color : tuple or Color
        The `Color` to use when drawing the sphere edges. If `None`, then no
        sphere edges are drawn.
    """
    def __init__(self, radius=1.0, cols=30, rows=30, vertex_colors=None,
                 face_colors=None, color=(0.5, 0.5, 1, 1), edge_color=None):

        mesh = create_sphere(cols, rows, radius=radius)

        MeshVisual.__init__(self, mesh.get_vertices(), mesh.get_faces(),
                            vertex_colors, face_colors, color)
        if edge_color:
            self._outline = MeshVisual(vertices['position'], outline_indices,
                                       color=edge_color, mode='lines')
        else:
            self._outline = None

        self.mesh = mesh

    @property
    def vertices(self):
        return self.mesh.get_vertices()

    @property
    def faces(self):
        return self.mesh.get_faces()

    def draw(self, transforms):
        """Draw the visual

        Parameters
        ----------
        transforms : instance of TransformSystem
            The transforms to use.
        """
        MeshVisual.draw(self, transforms)
        if self._outline is not None:
            set_state(polygon_offset=(1, 1), polygon_offset_fill=True)
            self._outline.draw(transforms)
