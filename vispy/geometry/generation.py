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


def create_plane(width=1, height=1, width_segments=1, height_segments=1,
                 direction='+z'):
    """ Generate vertices & indices for a filled and outlined plane.

    Parameters
    ----------
    width : float
        Plane width.
    height : float
        Plane height.
    width_segments : int
        Plane segments count along the width.
    height_segments : float
        Plane segments count along the height.
    direction: unicode
        ``{'-x', '+x', '-y', '+y', '-z', '+z'}``
        Direction the plane will be facing.

    Returns
    -------
    vertices : array
        Array of vertices suitable for use as a VertexBuffer.
    faces : array
        Indices to use to produce a filled plane.
    outline : array
        Indices to use to produce an outline of the plane.

    References
    ----------
    .. [1] Cabello, R. (n.d.). PlaneBufferGeometry.js. Retrieved May 12, 2015,
        from http://git.io/vU1Fh
    """

    x_grid = width_segments
    y_grid = height_segments

    x_grid1 = x_grid + 1
    y_grid1 = y_grid + 1

    # Positions, normals and texcoords.
    positions = np.zeros(x_grid1 * y_grid1 * 3)
    normals = np.zeros(x_grid1 * y_grid1 * 3)
    texcoords = np.zeros(x_grid1 * y_grid1 * 2)

    y = np.arange(y_grid1) * height / y_grid - height / 2
    x = np.arange(x_grid1) * width / x_grid - width / 2

    positions[::3] = np.tile(x, y_grid1)
    positions[1::3] = -np.repeat(y, x_grid1)

    normals[2::3] = 1

    texcoords[::2] = np.tile(np.arange(x_grid1) / x_grid, y_grid1)
    texcoords[1::2] = np.repeat(1 - np.arange(y_grid1) / y_grid, x_grid1)

    # Faces and outline.
    faces, outline = [], []
    for i_y in range(y_grid):
        for i_x in range(x_grid):
            a = i_x + x_grid1 * i_y
            b = i_x + x_grid1 * (i_y + 1)
            c = (i_x + 1) + x_grid1 * (i_y + 1)
            d = (i_x + 1) + x_grid1 * i_y

            faces.extend(((a, b, d), (b, c, d)))
            outline.extend(((a, b), (b, c), (c, d), (d, a)))

    positions = np.reshape(positions, (-1, 3))
    texcoords = np.reshape(texcoords, (-1, 2))
    normals = np.reshape(normals, (-1, 3))

    faces = np.reshape(faces, (-1, 3)).astype(np.uint32)
    outline = np.reshape(outline, (-1, 2)).astype(np.uint32)

    direction = direction.lower()
    if direction in ('-x', '+x'):
        shift, neutral_axis = 1, 0
    elif direction in ('-y', '+y'):
        shift, neutral_axis = -1, 1
    elif direction in ('-z', '+z'):
        shift, neutral_axis = 0, 2

    sign = -1 if '-' in direction else 1

    positions = np.roll(positions, shift, -1)
    normals = np.roll(normals, shift, -1) * sign
    colors = np.ravel(positions)
    colors = np.hstack((np.reshape(np.interp(colors,
                                             (np.min(colors),
                                              np.max(colors)),
                                             (0, 1)),
                                   positions.shape),
                        np.ones((positions.shape[0], 1))))
    colors[..., neutral_axis] = 0

    vertices = np.zeros(positions.shape[0],
                        [('position', np.float32, 3),
                         ('texcoord', np.float32, 2),
                         ('normal', np.float32, 3),
                         ('color', np.float32, 4)])

    vertices['position'] = positions
    vertices['texcoord'] = texcoords
    vertices['normal'] = normals
    vertices['color'] = colors

    return vertices, faces, outline


def create_box(width=1, height=1, depth=1, width_segments=1, height_segments=1,
               depth_segments=1, planes=None):
    """ Generate vertices & indices for a filled and outlined box.

    Parameters
    ----------
    width : float
        Box width.
    height : float
        Box height.
    depth : float
        Box depth.
    width_segments : int
        Box segments count along the width.
    height_segments : float
        Box segments count along the height.
    depth_segments : float
        Box segments count along the depth.
    planes: array_like
        Any combination of ``{'-x', '+x', '-y', '+y', '-z', '+z'}``
        Included planes in the box construction.

    Returns
    -------
    vertices : array
        Array of vertices suitable for use as a VertexBuffer.
    faces : array
        Indices to use to produce a filled box.
    outline : array
        Indices to use to produce an outline of the box.
    """

    planes = (('+x', '-x', '+y', '-y', '+z', '-z')
              if planes is None else
              [d.lower() for d in planes])

    w_s, h_s, d_s = width_segments, height_segments, depth_segments

    planes_m = []
    if '-z' in planes:
        planes_m.append(create_plane(width, depth, w_s, d_s, '-z'))
        planes_m[-1][0]['position'][..., 2] -= height / 2
    if '+z' in planes:
        planes_m.append(create_plane(width, depth, w_s, d_s, '+z'))
        planes_m[-1][0]['position'][..., 2] += height / 2

    if '-y' in planes:
        planes_m.append(create_plane(height, width, h_s, w_s, '-y'))
        planes_m[-1][0]['position'][..., 1] -= depth / 2
    if '+y' in planes:
        planes_m.append(create_plane(height, width, h_s, w_s, '+y'))
        planes_m[-1][0]['position'][..., 1] += depth / 2

    if '-x' in planes:
        planes_m.append(create_plane(depth, height, d_s, h_s, '-x'))
        planes_m[-1][0]['position'][..., 0] -= width / 2
    if '+x' in planes:
        planes_m.append(create_plane(depth, height, d_s, h_s, '+x'))
        planes_m[-1][0]['position'][..., 0] += width / 2

    positions = np.zeros((0, 3), dtype=np.float32)
    texcoords = np.zeros((0, 2), dtype=np.float32)
    normals = np.zeros((0, 3), dtype=np.float32)

    faces = np.zeros((0, 3), dtype=np.uint32)
    outline = np.zeros((0, 2), dtype=np.uint32)

    offset = 0
    for vertices_p, faces_p, outline_p in planes_m:
        positions = np.vstack((positions, vertices_p['position']))
        texcoords = np.vstack((texcoords, vertices_p['texcoord']))
        normals = np.vstack((normals, vertices_p['normal']))

        faces = np.vstack((faces, faces_p + offset))
        outline = np.vstack((outline, outline_p + offset))
        offset += vertices_p['position'].shape[0]

    vertices = np.zeros(positions.shape[0],
                        [('position', np.float32, 3),
                         ('texcoord', np.float32, 2),
                         ('normal', np.float32, 3),
                         ('color', np.float32, 4)])

    colors = np.ravel(positions)
    colors = np.hstack((np.reshape(np.interp(colors,
                                             (np.min(colors),
                                              np.max(colors)),
                                             (0, 1)),
                                   positions.shape),
                        np.ones((positions.shape[0], 1))))

    vertices['position'] = positions
    vertices['texcoord'] = texcoords
    vertices['normal'] = normals
    vertices['color'] = colors

    return vertices, faces, outline


def _latitude(rows, cols, radius, offset):
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


def _ico(radius, subdivisions):
    # golden ratio
    t = (1.0 + np.sqrt(5.0))/2.0

    # vertices of a icosahedron
    verts = [(-1, t, 0),
             (1, t, 0),
             (-1, -t, 0),
             (1, -t, 0),
             (0, -1, t),
             (0, 1, t),
             (0, -1, -t),
             (0, 1, -t),
             (t, 0, -1),
             (t, 0, 1),
             (-t, 0, -1),
             (-t, 0, 1)]

    # faces of the icosahedron
    faces = [(0, 11, 5),
             (0, 5, 1),
             (0, 1, 7),
             (0, 7, 10),
             (0, 10, 11),
             (1, 5, 9),
             (5, 11, 4),
             (11, 10, 2),
             (10, 7, 6),
             (7, 1, 8),
             (3, 9, 4),
             (3, 4, 2),
             (3, 2, 6),
             (3, 6, 8),
             (3, 8, 9),
             (4, 9, 5),
             (2, 4, 11),
             (6, 2, 10),
             (8, 6, 7),
             (9, 8, 1)]

    def midpoint(v1, v2):
        return ((v1[0]+v2[0])/2, (v1[1]+v2[1])/2, (v1[2]+v2[2])/2)

    # subdivision
    for _ in range(subdivisions):
        for idx in range(len(faces)):
            i, j, k = faces[idx]
            a, b, c = verts[i], verts[j], verts[k]
            ab, bc, ca = midpoint(a, b), midpoint(b, c), midpoint(c, a)
            verts += [ab, bc, ca]
            ij, jk, ki = len(verts)-3, len(verts)-2, len(verts)-1
            faces.append([i, ij, ki])
            faces.append([ij, j, jk])
            faces.append([ki, jk, k])
            faces[idx] = [jk, ki, ij]
    verts = np.array(verts)
    faces = np.array(faces)

    # make each vertex to lie on the sphere
    lengths = np.sqrt((verts*verts).sum(axis=1))
    verts /= lengths[:, np.newaxis]/radius
    return MeshData(vertices=verts, faces=faces)


def _cube(rows, cols, depth, radius):
    # vertices and faces of tessellated cube
    verts, faces, _ = create_box(1, 1, 1, rows, cols, depth)
    verts = verts['position']

    # make each vertex to lie on the sphere
    lengths = np.sqrt((verts*verts).sum(axis=1))
    verts /= lengths[:, np.newaxis]/radius
    return MeshData(vertices=verts, faces=faces)


def create_sphere(rows=10, cols=10, depth=10, radius=1.0, offset=True,
                  subdivisions=3, method='latitude'):
    """Create a sphere
    Parameters
    ----------
    rows : int
        Number of rows (for method='latitude' and 'cube').
    cols : int
        Number of columns (for method='latitude' and 'cube').
    depth : int
        Number of depth segments (for method='cube').
    radius : float
        Sphere radius.
    offset : bool
        Rotate each row by half a column (for method='latitude').
    subdivisions : int
        Number of subdivisions to perform (for method='ico')
    method : str
        Method for generating sphere. Accepts 'latitude' for latitude-
        longitude, 'ico' for icosahedron, and 'cube' for cube based
        tessellation.

    Returns
    -------
    sphere : MeshData
        Vertices and faces computed for a spherical surface.
    """
    if method == 'latitude':
        return _latitude(rows, cols, radius, offset)
    elif method == 'ico':
        return _ico(radius, subdivisions)
    elif method == 'cube':
        return _cube(rows, cols, depth, radius)
    else:
        raise Exception("Invalid method. Accepts: 'latitude', 'ico', 'cube'")


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


def create_grid_mesh(xs, ys, zs):
    '''Generate vertices and indices for an implicitly connected mesh.

    The intention is that this makes it simple to generate a mesh
    from meshgrid data.

    Parameters
    ----------
    xs : ndarray
        A 2d array of x coordinates for the vertices of the mesh. Must
        have the same dimensions as ys and zs.
    ys : ndarray
        A 2d array of y coordinates for the vertices of the mesh. Must
        have the same dimensions as xs and zs.
    zs : ndarray
        A 2d array of z coordinates for the vertices of the mesh. Must
        have the same dimensions as xs and ys.

    Returns
    -------
    vertices : ndarray
        The array of vertices in the mesh.
    indices : ndarray
        The array of indices for the mesh.
    '''

    shape = xs.shape
    length = shape[0] * shape[1]

    vertices = np.zeros((length, 3))

    vertices[:, 0] = xs.reshape(length)
    vertices[:, 1] = ys.reshape(length)
    vertices[:, 2] = zs.reshape(length)

    basic_indices = np.array([0, 1, 1 + shape[1], 0,
                              0 + shape[1], 1 + shape[1]],
                             dtype=np.uint32)

    inner_grid_length = (shape[0] - 1) * (shape[1] - 1)

    offsets = np.arange(inner_grid_length)
    offsets += np.repeat(np.arange(shape[0] - 1), shape[1] - 1)
    offsets = np.repeat(offsets, 6)
    indices = np.resize(basic_indices, len(offsets)) + offsets

    indices = indices.reshape((len(indices) // 3, 3))

    return vertices, indices
