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
        The length(s) of the normals. If None, the length is set to the median
        length of the edges of the mesh.
    **kwargs : dict, optional
        Extra arguments to define the appearance of lines. Refer to
        :class:`~vispy.visuals.line.LineVisual`.
    """

    def __init__(self, meshdata, primitive='face', length=None, **kwargs):
        if primitive not in ('face', 'vertex'):
            raise ValueError('primitive must be "face" or "vertex", got %s'
                             % primitive)

        if primitive == 'face':
            normals = meshdata.get_face_normals()
        elif primitive == 'vertex':
            normals = meshdata.get_vertex_normals()
        norms = np.sqrt((normals ** 2).sum(axis=-1, keepdims=True))
        normals /= norms

        if length is None:
            face_corners = meshdata.get_vertices(indexed='faces')
            edges = np.stack((
                face_corners[:, 1, :] - face_corners[:, 0, :],
                face_corners[:, 2, :] - face_corners[:, 1, :],
                face_corners[:, 0, :] - face_corners[:, 2, :],
            ))
            edge_lengths = np.sqrt((edges ** 2).sum(axis=-1))
            length = np.median(edge_lengths)

        if primitive == 'face':
            origins = meshdata.get_vertices(indexed='faces')
            origins = origins.mean(axis=1)
        else:
            origins = meshdata.get_vertices()
        ends = origins + length * normals
        segments = np.hstack((origins, ends)).reshape(-1, 3)

        LineVisual.__init__(self, pos=segments, connect='segments', **kwargs)
