# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Nicolas P .Rougier
# Date:   04/03/2014
# -----------------------------------------------------------------------------
from __future__ import division

import numpy as np

from .meshdata import MeshData


def create_cube():
    """ Generate vertices & indices for a filled and outlined cube

    Returns
    -------
    vertices : array
        Array of vertices suitable for use as a VertexBuffer.
    filled : array
        Indices to use to produce a filled cube.
    outline : array
        Indices to use to produce an outline of the cube.
    """
    vtype = [('position', np.float32, 3),
             ('texcoord', np.float32, 2),
             ('normal', np.float32, 3),
             ('color',    np.float32, 4)]
    itype = np.uint32

    # Vertices positions
    p = np.array([[1, 1, 1], [-1, 1, 1], [-1, -1, 1], [1, -1, 1],
                  [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, -1]])

    # Face Normals
    n = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0],
                  [-1, 0, 1], [0, -1, 0], [0, 0, -1]])

    # Vertice colors
    c = np.array([[1, 1, 1, 1], [0, 1, 1, 1], [0, 0, 1, 1], [1, 0, 1, 1],
                  [1, 0, 0, 1], [1, 1, 0, 1], [0, 1, 0, 1], [0, 0, 0, 1]])

    # Texture coords
    t = np.array([[0, 0], [0, 1], [1, 1], [1, 0]])

    faces_p = [0, 1, 2, 3,
               0, 3, 4, 5,
               0, 5, 6, 1,
               1, 6, 7, 2,
               7, 4, 3, 2,
               4, 7, 6, 5]
    faces_c = [0, 1, 2, 3,
               0, 3, 4, 5,
               0, 5, 6, 1,
               1, 6, 7, 2,
               7, 4, 3, 2,
               4, 7, 6, 5]
    faces_n = [0, 0, 0, 0,
               1, 1, 1, 1,
               2, 2, 2, 2,
               3, 3, 3, 3,
               4, 4, 4, 4,
               5, 5, 5, 5]
    faces_t = [0, 1, 2, 3,
               0, 1, 2, 3,
               0, 1, 2, 3,
               3, 2, 1, 0,
               0, 1, 2, 3,
               0, 1, 2, 3]

    vertices = np.zeros(24, vtype)
    vertices['position'] = p[faces_p]
    vertices['normal'] = n[faces_n]
    vertices['color'] = c[faces_c]
    vertices['texcoord'] = t[faces_t]

    filled = np.resize(
        np.array([0, 1, 2, 0, 2, 3], dtype=itype), 6 * (2 * 3))
    filled += np.repeat(4 * np.arange(6, dtype=itype), 6)
    filled = filled.reshape((len(filled) // 3, 3))

    outline = np.resize(
        np.array([0, 1, 1, 2, 2, 3, 3, 0], dtype=itype), 6 * (2 * 4))
    outline += np.repeat(4 * np.arange(6, dtype=itype), 8)

    return vertices, filled, outline


def create_sphere(rows, cols, radius=1.0, offset=True):
    """Create a sphere

    Parameters
    ----------
    rows : int
        Number of rows.
    cols : int
        Number of columns.
    radius : float
        Sphere radius.
    offset : bool
        Rotate each row by half a column.

    Returns
    -------
    sphere : MeshData
        Vertices and faces computed for a spherical surface.
    """
    verts = np.empty((rows+1, cols, 3), dtype=np.float32)

    # compute vertices
    phi = (np.arange(rows+1) * np.pi / rows).reshape(rows+1, 1)
    s = radius * np.sin(phi)
    verts[..., 2] = radius * np.cos(phi)
    th = ((np.arange(cols) * 2 * np.pi / cols).reshape(1, cols))
    if offset:
        # rotate each row by 1/2 column
        th = th + ((np.pi / cols) * np.arange(rows+1).reshape(rows+1, 1))
    verts[..., 0] = s * np.cos(th)
    verts[..., 1] = s * np.sin(th)
    # remove redundant vertices from top and bottom
    verts = verts.reshape((rows+1)*cols, 3)[cols-1:-(cols-1)]

    # compute faces
    faces = np.empty((rows*cols*2, 3), dtype=np.uint32)
    rowtemplate1 = (((np.arange(cols).reshape(cols, 1) +
                      np.array([[1, 0, 0]])) % cols) +
                    np.array([[0, 0, cols]]))
    rowtemplate2 = (((np.arange(cols).reshape(cols, 1) +
                      np.array([[1, 0, 1]])) % cols) +
                    np.array([[0, cols, cols]]))
    for row in range(rows):
        start = row * cols * 2
        faces[start:start+cols] = rowtemplate1 + row * cols
        faces[start+cols:start+(cols*2)] = rowtemplate2 + row * cols
    # cut off zero-area triangles at top and bottom
    faces = faces[cols:-cols]

    # adjust for redundant vertices that were removed from top and bottom
    vmin = cols-1
    faces[faces < vmin] = vmin
    faces -= vmin
    vmax = verts.shape[0]-1
    faces[faces > vmax] = vmax
    return MeshData(vertices=verts, faces=faces)


def create_cylinder(rows, cols, radius=[1.0, 1.0], length=1.0, offset=False):
    """Create a cylinder

    Parameters
    ----------
    rows : int
        Number of rows.
    cols : int
        Number of columns.
    radius : tuple of float
        Cylinder radii.
    length : float
        Length of the cylinder.
    offset : bool
        Rotate each row by half a column.

    Returns
    -------
    cylinder : MeshData
        Vertices and faces computed for a cylindrical surface.
    """
    verts = np.empty((rows+1, cols, 3), dtype=np.float32)
    if isinstance(radius, int):
        radius = [radius, radius]  # convert to list
    # compute vertices
    th = np.linspace(2 * np.pi, 0, cols).reshape(1, cols)
    # radius as a function of z
    r = np.linspace(radius[0], radius[1], num=rows+1,
                    endpoint=True).reshape(rows+1, 1)
    verts[..., 2] = np.linspace(0, length, num=rows+1,
                                endpoint=True).reshape(rows+1, 1)  # z
    if offset:
        # rotate each row by 1/2 column
        th = th + ((np.pi / cols) * np.arange(rows+1).reshape(rows+1, 1))
    verts[..., 0] = r * np.cos(th)  # x = r cos(th)
    verts[..., 1] = r * np.sin(th)  # y = r sin(th)
    # just reshape: no redundant vertices...
    verts = verts.reshape((rows+1)*cols, 3)
    # compute faces
    faces = np.empty((rows*cols*2, 3), dtype=np.uint32)
    rowtemplate1 = (((np.arange(cols).reshape(cols, 1) +
                      np.array([[0, 1, 0]])) % cols) +
                    np.array([[0, 0, cols]]))
    rowtemplate2 = (((np.arange(cols).reshape(cols, 1) +
                      np.array([[0, 1, 1]])) % cols) +
                    np.array([[cols, 0, cols]]))
    for row in range(rows):
        start = row * cols * 2
        faces[start:start+cols] = rowtemplate1 + row * cols
        faces[start+cols:start+(cols*2)] = rowtemplate2 + row * cols

    return MeshData(vertices=verts, faces=faces)


def create_cone(cols, radius=1.0, length=1.0):
    """Create a cone

    Parameters
    ----------
    cols : int
        Number of faces.
    radius : float
        Base cone radius.
    length : float
        Length of the cone.

    Returns
    -------
    cone : MeshData
        Vertices and faces computed for a cone surface.
    """
    verts = np.empty((cols+1, 3), dtype=np.float32)
    # compute vertexes
    th = np.linspace(2 * np.pi, 0, cols+1).reshape(1, cols+1)
    verts[:-1, 2] = 0.0
    verts[:-1, 0] = radius * np.cos(th[0, :-1])  # x = r cos(th)
    verts[:-1, 1] = radius * np.sin(th[0, :-1])  # y = r sin(th)
    # Add the extremity
    verts[-1, 0] = 0.0
    verts[-1, 1] = 0.0
    verts[-1, 2] = length
    verts = verts.reshape((cols+1), 3)  # just reshape: no redundant vertices
    # compute faces
    faces = np.empty((cols, 3), dtype=np.uint32)
    template = np.array([[0, 1]])
    for pos in range(cols):
        faces[pos, :-1] = template + pos
    faces[:, 2] = cols
    faces[-1, 1] = 0

    return MeshData(vertices=verts, faces=faces)


def create_arrow(rows, cols, radius=0.1, length=1.0,
                 cone_radius=None, cone_length=None):
    """Create a 3D arrow using a cylinder plus cone

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

    Returns
    -------
    arrow : MeshData
        Vertices and faces computed for a cone surface.
    """
    # create the cylinder
    md_cyl = None
    if cone_radius is None:
        cone_radius = radius*2.0
    if cone_length is None:
        con_L = length/3.0
        cyl_L = length*2.0/3.0
    else:
        cyl_L = max(0, length - cone_length)
        con_L = min(cone_length, length)
    if cyl_L != 0:
        md_cyl = create_cylinder(rows, cols, radius=[radius, radius],
                                 length=cyl_L)
    # create the cone
    md_con = create_cone(cols, radius=cone_radius, length=con_L)
    verts = md_con.get_vertices()
    nbr_verts_con = verts.size//3
    faces = md_con.get_faces()
    if md_cyl is not None:
        trans = np.array([[0.0, 0.0, cyl_L]])
        verts = np.vstack((verts+trans, md_cyl.get_vertices()))
        faces = np.vstack((faces, md_cyl.get_faces()+nbr_verts_con))

    return MeshData(vertices=verts, faces=faces)
