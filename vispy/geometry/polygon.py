# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np

from .triangulation import Triangulation


class PolygonData(object):
    """Class for handling 2D polygon data.
    
    Parameters
    ----------
    vertices : array | None
        (n_verts, 3) array of vertex coordinates.
    edges : array | None
        Optional (n_edges, 2) array of indices into *vertices*. If None,
        then edges will be automatically generated in a single path 
        that traverses the vertices in order and loops back to the first
        veretx.
    """
    def __init__(self, vertices=None, edges=None, faces=None):
        self._vertices = vertices
        self._edges = edges
        self._auto_edges = None
        self.triangulation = None

    @property
    def faces(self):
        """A tuple of two arrays (vertices, faces) describing the mesh triangles
        needed to fill this polygon.
        
        Faces are generated using vispy.triangulation.
        """
        if self.triangulation is None:
            if self._vertices is None:
                return None

            self.triangulation = Triangulation(self.vertices, self.edges)
            self.triangulation.triangulate()
        return self.triangulation.pts, self.triangulation.tris

    @property
    def vertices(self):
        """Return an array (Nf, 3) of vertices

        If only faces exist, the function computes the vertices and
        returns them.
        If no vertices or faces are specified, the function returns None.
        """
        return self._vertices

    @vertices.setter
    def vertices(self, v):
        """
        If vertices and faces are incompatible, this will generate faces
        from these vertices and set them.
        """
        self._vertices = v
        self._auto_edges = None
        self.triangulation = None

    @property
    def edges(self):
        """An array (n_edges, 2) of indexes into self.vertices specifying
        the bounding edges of the polygon.
        
        If no edges were manually specified, then this property is generated
        by simply connecting the vertices in order to form a loop.
        """
        if self._edges is not None:
            return self._edges
        
        if self._auto_edges is None:
            if self._vertices is None:
                return None
            npts = self._vertices.shape[0]
            if np.any(self._vertices[0] != self._vertices[1]):
                # start != end, so edges must wrap around to beginning.
                edges = np.empty((npts, 2), dtype=np.uint32)
                edges[:, 0] = np.arange(npts)
                edges[:, 1] = edges[:, 0] + 1
                edges[-1, 1] = 0
            else:
                # start == end; no wrapping required.
                edges = np.empty((npts-1, 2), dtype=np.uint32)
                edges[:, 0] = np.arange(npts)
                edges[:, 1] = edges[:, 0] + 1
            self._auto_edges = edges
        return self._auto_edges

    @edges.setter
    def edges(self, edges):
        self._edges = edges
        if edges is not None:
            self._auto_edges = None
        self.triangulation = None
