# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Reading and writing of data like images and meshes.
"""

import os
import bz2
import numpy as np

THISDIR = os.path.dirname(os.path.abspath(__file__))
RESOURCE_DIR = os.path.join(os.path.dirname(THISDIR), 'resources')


# So we can demo image data without needing an image reading library
def lena():
    """ Return the lena image (512x512 RGB).
    """
    with open(os.path.join(RESOURCE_DIR, 'lena.bz2'), 'rb') as f:
        bb = f.read()
    a = np.frombuffer(bz2.decompress(bb), np.uint8)
    a.shape = 512, 512, 3
    return a


def read_mesh(fname, format=None):
    """ Read mesh data from file.
    returns (vertices, faces, normals, texcoords)
    texcoords and faces may be None.
    
    Mesh files that ship with vispy always work: 'triceratops.obj'.
    """
    # Check file
    if not os.path.isfile(fname):
        # Maybe we have it?
        fname_ = os.path.join(RESOURCE_DIR, fname)
        if os.path.isfile(fname_):
            fname = fname_
        else:
            raise ValueError('File does not exist: %s' % fname)
    
    # Check format
    if format is None:
        format = os.path.splitext(fname)[1]
    format = format.strip('. ').upper()
    
    if format == 'OBJ':
        from .wavefront import WavefrontReader
        return WavefrontReader.read(fname)
    elif not format:
        raise ValueError('read_mesh needs could not determine format.')
    else:
        raise ValueError('read_mesh does not understand format %s.' % format)
        
