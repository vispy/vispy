# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np
from scipy.spatial import Delaunay


class PolygonData(object):
    """
    Polygon class for data handling
    """
    def __init__(self, vertices=None, edges=None, faces=None):
        """
        Parameters
        ----------
        vertexes        (Nv, 3) array of vertex coordinates.
                        If faces is not specified, then this will instead be
                        interpreted as (Nf, 3, 3) array of coordinates.
        faces           (Nf, 3) array of indexes into the vertex array.
        edges           (Nv, 2) array of constraining edges specified by vertex
                        indices.
        
        All arguments are optional.
        """
        self._vertices = vertices
        self._edges = edges
        self._faces = faces
        self._convex_hull = None

    @property  
    def faces(self):
        """Return an array (Nf, 3) of vertex indexes, three per triangular
        face in the mesh.
        
        If faces have not been computed for this mesh, the function
        computes them.
        If no vertices or faces are specified, the function returns None.
        """

        if self._faces is None:
            if self._vertices is None:
                return None
            self.triangulate()
        return self._faces

    @faces.setter
    def faces(self, f):
        """
        If vertices and faces are incompatible, this will generate vertices
        from these faces and set them.
        """
        self._faces = f

    @property  
    def vertices(self):
        """Return an array (Nf, 3) of vertices.
        
        If only faces exist, the function computes the vertices and
        returns them.
        If no vertices or faces are specified, the function returns None.
        """

        if self._faces is None:
            if self._vertices is None:
                return None
            self.triangulate()
        return self._vertices

    @vertices.setter
    def vertices(self, v):
        """
        If vertices and faces are incompatible, this will generate faces
        from these vertices and set them.
        """
        self._vertices = v

    @property  
    def edges(self):
        """Return an array (Nv, 2) of vertex indices.

        If no vertices or faces are specified, the function returns None.
        """
        return self._edges

    @edges.setter
    def edges(self, e):
        """
        Ensures that all edges are valid.
        """
        self._edges = e

    @property  
    def convex_hull(self):
        """Return an array of vertex indexes representing the convex hull.
        
        If faces have not been computed for this mesh, the function
        computes them.
        If no vertices or faces are specified, the function returns None.
        """

        if self._faces is None:
            if self._vertices is None:
                return None
            self.triangulate()
        return self._convex_hull

    def triangulate(self):
        # To be replaced soon to remove scipy dependency
        """
        Triangulates the set of vertices and stores the triangles in faces and
        the convex hull in convex_hull.
        """
        if self._vertices is None:
            return
        pos2 = np.delete(self._vertices, 2, 1)
        tri = Delaunay(pos2)
        self._faces = tri.simplices
        self._convex_hull = tri.convex_hull

    def add_vertex(self, vertex):
        """
        Adds given vertex and retriangulates to generate new faces.
        """
        pass
