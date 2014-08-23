# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Reading and writing of data like images and meshes.
"""

import os
from os import path as op

from .wavefront import WavefrontReader, WavefrontWriter
from .datasets import DATA_DIR


def read_mesh(fname, format=None):
    """Read mesh data from file.

    Parameters
    ----------
    fname : str
        File name to read.
    format : str | None
        Format of file to read in. Currently only ``"obj"`` is supported.
        If None, format will be inferred from the filename.

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

    Notes
    -----
    Mesh files that ship with vispy always work, such as 'triceratops.obj'.
    """
    # Check file
    if not op.isfile(fname):
        # Maybe we have it?
        fname_ = op.join(DATA_DIR, fname)
        if op.isfile(fname_):
            fname = fname_
        else:
            raise ValueError('File does not exist: %s' % fname)

    # Check format
    if format is None:
        format = op.splitext(fname)[1]
    format = format.strip('. ').upper()

    if format == 'OBJ':
        return WavefrontReader.read(fname)
    elif not format:
        raise ValueError('read_mesh needs could not determine format.')
    else:
        raise ValueError('read_mesh does not understand format %s.' % format)


def write_mesh(fname, vertices, faces, normals, texcoords, name='',
               format='obj', overwrite=False):
    """ Write mesh data to file.

    Parameters
    ----------
    fname : str
        Filename to write.
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
    """
    # Check file
    if op.isfile(fname):
        if not overwrite:
            raise IOError('file "%s" exists, use overwrite=True' % fname)
        else:
            os.remove(fname)

    # Check format
    if format not in ('obj'):
        raise ValueError('Only "obj" format writing currently supported')
    WavefrontWriter.write(fname, vertices, faces, normals, texcoords, name)
