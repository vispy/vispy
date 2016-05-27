# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from ..geometry import create_sphere
from .mesh import MeshVisual
from .visual import CompoundVisual


class SphereVisual(CompoundVisual):
    """Visual that displays a sphere

    Parameters
    ----------
    radius : float
        The size of the sphere.
    cols : int
        Number of cols that make up the sphere mesh
        (for method='latitude' and 'cube').
    rows : int
        Number of rows that make up the sphere mesh
        (for method='latitude' and 'cube').
    depth : int
        Number of depth segments that make up the sphere mesh
        (for method='cube').
    subdivisions : int
        Number of subdivisions to perform (for method='ico').
    method : str
        Method for generating sphere. Accepts 'latitude' for
        latitude-longitude, 'ico' for icosahedron, and 'cube'
        for cube based tessellation.
    vertex_colors : ndarray
        Same as for `MeshVisual` class.
        See `create_sphere` for vertex ordering.
    face_colors : ndarray
        Same as for `MeshVisual` class.
        See `create_sphere` for vertex ordering.
    color : Color
        The `Color` to use when drawing the sphere faces.
    edge_color : tuple or Color
        The `Color` to use when drawing the sphere edges. If `None`, then no
        sphere edges are drawn.
    """
    def __init__(self, radius=1.0, cols=30, rows=30, depth=30, subdivisions=3,
                 method='latitude', vertex_colors=None, face_colors=None,
                 color=(0.5, 0.5, 1, 1), edge_color=None, **kwargs):

        mesh = create_sphere(cols, rows, depth, radius=radius,
                             subdivisions=subdivisions, method=method)

        self._mesh = MeshVisual(vertices=mesh.get_vertices(),
                                faces=mesh.get_faces(),
                                vertex_colors=vertex_colors,
                                face_colors=face_colors, color=color)
        if edge_color:
            self._border = MeshVisual(vertices=mesh.get_vertices(),
                                      faces=mesh.get_edges(),
                                      color=edge_color, mode='lines')
        else:
            self._border = MeshVisual()

        CompoundVisual.__init__(self, [self._mesh, self._border], **kwargs)
        self.mesh.set_gl_state(polygon_offset_fill=True,
                               polygon_offset=(1, 1), depth_test=True)

    @property
    def mesh(self):
        """The vispy.visuals.MeshVisual that used to fil in.
        """
        return self._mesh

    @property
    def border(self):
        """The vispy.visuals.MeshVisual that used to draw the border.
        """
        return self._border
