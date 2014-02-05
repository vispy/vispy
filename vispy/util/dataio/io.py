# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Reading and writing of data like images and meshes.
"""

import os
import bz2
import numpy as np

from .wavefront import WavefrontReader, WavefrontWriter

THISDIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(THISDIR), '..', 'data')


# So we can demo image data without needing an image reading library
def crate():
    """ Return an image of a crate (256x256 RGB).
    """
    with open(os.path.join(DATA_DIR, 'crate.bz2'), 'rb') as f:
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
    if not os.path.isfile(fname):
        # Maybe we have it?
        fname_ = os.path.join(DATA_DIR, fname)
        if os.path.isfile(fname_):
            fname = fname_
        else:
            raise ValueError('File does not exist: %s' % fname)

    # Check format
    if format is None:
        format = os.path.splitext(fname)[1]
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
    if os.path.isfile(fname):
        if not overwrite:
            raise IOError('file "%s" exists, use overwrite=True' % fname)
        else:
            os.remove(fname)

    # Check format
    if format not in ['obj']:
        raise ValueError('Only "obj" format writing currently supported')
    return WavefrontWriter.write(fname, vertices, faces, normals, texcoords,
                                 name)


def imread(filename, format=None):
    """ Function to read image data. Requires imageio or PIL.
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
    """ Function to save image data. Requires imageio or PIL.
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
