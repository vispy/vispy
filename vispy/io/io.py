# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Reading and writing of data like images and meshes.
"""

import os
from os import path as op
import bz2
import numpy as np

from .wavefront import WavefrontReader, WavefrontWriter
from ..ext.png import Reader

DATA_DIR = op.join(op.dirname(__file__), '_data')


# So we can demo image data without needing an image reading library
def crate():
    """ Return an image of a crate (256x256 RGB).
    """
    with open(op.join(DATA_DIR, 'crate.bz2'), 'rb') as f:
        bb = f.read()
    a = np.frombuffer(bz2.decompress(bb), np.uint8)
    a.shape = 256, 256, 3
    return a


# def _write_image_blob(im, fname):
#     bb = bz2.compress(im.tostring())
#     with open(os.path.join(DATA_DIR, fname), 'wb') as f:
#         f.write(bb)


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
    """
    # Check file
    if op.isfile(fname):
        if not overwrite:
            raise IOError('file "%s" exists, use overwrite=True' % fname)
        else:
            os.remove(fname)

    # Check format
    if format not in ['obj']:
        raise ValueError('Only "obj" format writing currently supported')
    return WavefrontWriter.write(fname, vertices, faces, normals, texcoords,
                                 name)


def read_png(filename):
    """Helper to read a PNG file to RGB8 or RGBA8 (with no external deps)

    Parameters
    ----------
    filename : str
        File to read.

    Returns
    -------
    data : array
        Image data.
    """
    x = Reader(filename)
    try:
        alpha = x.asDirect()[3]['alpha']
        if alpha:
            y = x.asRGBA8()[2]
            n = 4
        else:
            y = x.asRGB8()[2]
            n = 3
        y = np.array([yy for yy in y], np.uint8)
    finally:
        x.file.close()
    y.shape = (y.shape[0], y.shape[1] // n, n)
    return y


def imread(filename, format=None):
    """Function to read image data. Requires imageio or PIL.

    Parameters
    ----------
    filename : str
        Filename to read.
    format : str | None
        Format of the file. If None, it will be inferred from the filename.

    Returns
    -------
    data : array
        Image data.
    """
    imageio, PIL = _check_img_lib()
    if imageio is not None:
        return imageio.imread(filename, format)
    elif PIL is not None:
        im = PIL.Image.open(filename)
        if im.mode == 'P':
            im = im.convert()
        # Make numpy array
        a = np.asarray(im)
        if len(a.shape) == 0:
            raise MemoryError("Too little memory to convert PIL image to "
                              "array")
        return a
    else:
        raise RuntimeError("imread requires the imageio or PIL package.")


def imsave(filename, im, format=None):
    """Function to save image data. Requires imageio or PIL.

    Parameters
    ----------
    filename : str
        Filename to write.
    im : array
        Image data.
    format : str | None
        Format of the file. If None, it will be inferred from the filename.
    """
    # Import imageio or PIL
    imageio, PIL = _check_img_lib()
    if imageio is not None:
        return imageio.imsave(filename, im, format)
    elif PIL is not None:
        pim = PIL.Image.fromarray(im)
        pim.save(filename, format)
    else:
        raise RuntimeError("imsave requires the imageio or PIL package.")


def _check_img_lib():
    """Utility to search for imageio or PIL"""
    # Import imageio or PIL
    imageio = PIL = None
    try:
        import imageio
    except ImportError:
        try:
            import PIL.Image
        except ImportError:
            pass
    return imageio, PIL
