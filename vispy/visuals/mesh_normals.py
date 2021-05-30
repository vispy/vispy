# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""A visual for displaying mesh normals as lines."""

import numpy as np

from . import LineVisual


class MeshNormalsVisual(LineVisual):
    """Display mesh normals as lines.

    Parameters
    ----------
    meshdata : instance of MeshData | None
        The meshdata.
    primitive : {'face', 'vertex'}
        The primitive type on which to compute and display the normals.
    length : None or float or array-like, optional
        The length(s) of the normals. If None, the length is computed with
        `length_method`.
    length_method : {'median_edge', 'max_extent'}, default='median_edge'
        The method to compute the length of the normals (when `length=None`).
        Methods: 'median_edge', the median edge length; 'max_extent', the
        maximum side length of the bounding box of the mesh.
    length_scale : float, default=1.0
        A scale factor applied to the length computed with `length_method`.
    **kwargs : dict, optional
        Extra arguments to define the appearance of lines. Refer to
        :class:`~vispy.visuals.line.LineVisual`.
    """

    def __init__(self, meshdata, primitive='face', length=None,
                 length_method='median_edge', length_scale=1.0, **kwargs):
        if primitive not in ('face', 'vertex'):
            raise ValueError('primitive must be "face" or "vertex", got %s'
                             % primitive)

        if primitive == 'face':
            normals = meshdata.get_face_normals()
        elif primitive == 'vertex':
            normals = meshdata.get_vertex_normals()
        norms = np.sqrt((normals ** 2).sum(axis=-1, keepdims=True))
        unit_normals = normals / norms

        if length is None and length_method == 'median_edge':
            face_corners = meshdata.get_vertices(indexed='faces')
            edges = np.stack((
                face_corners[:, 1, :] - face_corners[:, 0, :],
                face_corners[:, 2, :] - face_corners[:, 1, :],
                face_corners[:, 0, :] - face_corners[:, 2, :],
            ))
            edge_lengths = np.sqrt((edges ** 2).sum(axis=-1))
            length = np.median(edge_lengths)
        elif length is None and length_method == 'max_extent':
            vertices = meshdata.get_vertices()
            max_extent = np.max(vertices.max(axis=0) - vertices.min(axis=0))
            length = max_extent
        length *= length_scale

        if primitive == 'face':
            origins = meshdata.get_vertices(indexed='faces')
            origins = origins.mean(axis=1)
        elif primitive == 'vertex':
            origins = meshdata.get_vertices()
        ends = origins + length * unit_normals
        segments = np.hstack((origins, ends)).reshape(-1, 3)

        LineVisual.__init__(self, pos=segments, connect='segments', **kwargs)
