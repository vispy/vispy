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
    meshdata : instance of :class:`~vispy.geometry.meshdata.MeshData`
        The mesh data.
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
        :class:`~vispy.visuals.line.line.LineVisual`.

    Examples
    --------
    Create a :class:`~vispy.visuals.mesh.MeshVisual` on which to display
    the normals and get the :class:`~vispy.geometry.meshdata.MeshData`:

    >>> mesh = MeshVisual(vertices=vertices, faces=faces, ...)
    >>> meshdata = mesh.mesh_data

    Create a visual for the mesh normals:

    >>> normals = MeshNormalsVisual(meshdata)

    Display the face normals:

    >>> MeshNormalsVisual(..., primitive='face')
    >>> MeshNormalsVisual(...)  # equivalent (default values)

    Display the vertex normals:

    >>> MeshNormalsVisual(..., primitive='vertex')

    Fixed length for all normals:

    >>> MeshNormalsVisual(..., length=0.25)

    Individual length per normal:

    >>> lengths = np.array([0.5, 0.2, 0.7, ..., 0.7], dtype=float)
    >>> MeshNormalsVisual(..., length=lengths)
    >>> assert len(lengths) == len(faces)  # for face normals
    >>> assert len(lengths) == len(vertices)  # for vertex normals

    Normals at about the length of a triangle:

    >>> MeshNormalsVisual(..., length_method='median_edge', length_scale=1.0)
    >>> MeshNormalsVisual(...)  # equivalent (default values)

    Normals at about 10% the size of the mesh:

    >>> MeshNormalsVisual(..., length_method='max_extent', length_scale=0.1)
    """

    def __init__(self, meshdata=None, primitive='face', length=None,
                 length_method='median_edge', length_scale=1.0, **kwargs):
        self._previous_meshdata = None
        super().__init__(connect='segments')
        self.set_data(meshdata, primitive, length, length_method, length_scale, **kwargs)

    def set_data(self, meshdata=None, primitive='face', length=None,
                 length_method='median_edge', length_scale=1.0, **kwargs):
        """Set the data used to draw this visual

        Parameters
        ----------
        meshdata : instance of :class:`~vispy.geometry.meshdata.MeshData`
            The mesh data.
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
            :class:`~vispy.visuals.line.line.LineVisual`.
        """
        if meshdata is None:
            meshdata = self._previous_meshdata

        if meshdata is None or meshdata.is_empty():
            normals = None
        elif primitive == 'face':
            normals = meshdata.get_face_normals()
        elif primitive == 'vertex':
            normals = meshdata.get_vertex_normals()
        else:
            raise ValueError('primitive must be "face" or "vertex", got %s'
                             % primitive)

        # remove connect from kwargs to make sure we don't change it
        kwargs.pop('connect', None)

        if normals is None:
            super().set_data(pos=np.empty((0, 3), dtype=np.float32), connect='segments', **kwargs)
            return

        self._previous_meshdata = meshdata

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

        # Ensure the broadcasting if the input is an `(n,)` array.
        length = np.atleast_1d(length)
        length = length[:, None]

        ends = origins + length * unit_normals
        segments = np.hstack((origins, ends)).reshape(-1, 3)

        super().set_data(pos=segments, connect='segments', **kwargs)
