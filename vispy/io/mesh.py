# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Reading and writing of data like images and meshes.
"""

from os import path as op

from .wavefront import WavefrontReader, WavefrontWriter


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
    elif not format:
        raise ValueError('read_mesh needs could not determine format.')
    else:
        raise ValueError('read_mesh does not understand format %s.' % fmt)


def write_mesh(fname, vertices, faces, normals, texcoords, name='',
               format='obj', overwrite=False, reshape_faces=True):
    """ Write mesh data to file.

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

    # Check format
    if format not in ('obj'):
        raise ValueError('Only "obj" format writing currently supported')
    WavefrontWriter.write(fname, vertices, faces,
                          normals, texcoords, name, reshape_faces)
