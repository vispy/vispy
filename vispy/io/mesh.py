# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""Reading and writing of data like images and meshes."""

import os
from os import path as op

from .wavefront import WavefrontReader, WavefrontWriter
from .stl import load_stl


def read_mesh(fname):
    """Read mesh data from file.

    Parameters
    ----------
    fname : str
        File name to read. Format will be inferred from the filename.
        Currently only '.obj' and '.obj.gz' are supported.

    Returns
    -------
    vertices : array
        Vertices.
    faces : array | None
        Triangle face definitions.
    normals : array
        Normals for the mesh.
    texcoords : array | None
        Texture coordinates.
    """
    # Check format
    fmt = op.splitext(fname)[1].lower()
    if fmt == '.gz':
        fmt = op.splitext(op.splitext(fname)[0])[1].lower()

    if fmt in ('.obj'):
        return WavefrontReader.read(fname)
    elif fmt in ('.stl'):
        file_obj = open(fname, mode='rb')
        mesh = load_stl(file_obj)
        vertices = mesh['vertices']
        faces = mesh['faces']
        normals = mesh['face_normals']
        texcoords = None
        return vertices, faces, normals, texcoords
    else:
        try:
            import meshio
        except ImportError:
            raise ValueError('read_mesh does not understand format %s.' % fmt)

        try:
            mesh = meshio.read(fname)
        except meshio.ReadError:
            raise ValueError('read_mesh does not understand format %s.' % fmt)

        triangles = mesh.get_cells_type("triangle")
        if len(triangles) == 0:
            raise ValueError('mesh file does not contain triangles.')

        return mesh.points, triangles, None, None


def write_mesh(fname, vertices, faces, normals, texcoords, name='',
               format=None, overwrite=False, reshape_faces=True):
    """Write mesh data to file.

    Parameters
    ----------
    fname : str
        Filename to write. Must end with ".obj" or ".gz".
    vertices : array
        Vertices.
    faces : array | None
        Triangle face definitions.
    normals : array
        Normals for the mesh.
    texcoords : array | None
        Texture coordinates.
    name : str
        Name of the object.
    format : str
        Currently only "obj" is supported.
    overwrite : bool
        If the file exists, overwrite it.
    reshape_faces : bool
        Reshape the `faces` array to (Nf, 3). Set to `False`
        if you need to write a mesh with non triangular faces.
    """
    # Check file
    if op.isfile(fname) and not overwrite:
        raise IOError('file "%s" exists, use overwrite=True' % fname)

    if format is None:
        format = os.path.splitext(fname)[1][1:]

    # Check format
    if format == 'obj':
        WavefrontWriter.write(fname, vertices, faces,
                              normals, texcoords, name, reshape_faces)
        return

    try:
        import meshio
    except ImportError:
        raise ValueError('write_mesh does not understand format %s.' % format)

    cell_data = {}
    if normals is not None:
        cell_data["normals"] = [normals]
    if texcoords is not None:
        cell_data["texcoords"] = [texcoords]

    mesh = meshio.Mesh(vertices, [("triangle", faces)], cell_data=cell_data)

    try:
        mesh.write(fname, file_format=format)
    except meshio.WriteError:
        raise ValueError('write_mesh does not understand format %s.' % format)
