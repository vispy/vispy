# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Reading and writing of data like images and meshes.
"""

import os
import bz2
import numpy as np

THISDIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(THISDIR), '../data')


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
    """ Read mesh data from file.
    returns (vertices, faces, normals, texcoords)
    texcoords and faces may be None.
    
    Mesh files that ship with vispy always work: 'triceratops.obj'.
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
        from .wavefront import WavefrontReader
        return WavefrontReader.read(fname)
    elif not format:
        raise ValueError('read_mesh needs could not determine format.')
    else:
        raise ValueError('read_mesh does not understand format %s.' % format)


def imread(filename, format=None):
    """ Function to read image data. Requires imageio or PIL.
    """
    # Import imageio or PIL
    imageio = PIL = None
    try:
        import imageio
    except ImportError:
        try:
            import PIL.Image
        except ImportError:
            pass
     
    if imageio is not None:
        return imageio.imread(filename, format)
    elif PIL is not None:
        im = PIL.Image.open(filename)
        if im.mode == 'P':
            im = im.convert()
        # Make numpy array
        a = np.asarray(im)
        if len(a.shape)==0:
            raise MemoryError("Too little memory to convert PIL image to array")
    else:
        raise RuntimeError("imread requires the imageio or PIL package.")


def imsave(filename, im, format=None):
    """ Function to save image data. Requires imageio or PIL.
    """
    # Import imageio or PIL
    imageio = PIL = None
    try:
        import imageio
    except ImportError:
        try:
            import PIL.Image
        except ImportError:
            pass
     
    if imageio is not None:
        return imageio.imsave(filename, im, format)
    elif PIL is not None:
        pim = PIL.Image.fromarray(im)
        pim.save(filename, format)
    else:
        raise RuntimeError("imsave requires the imageio or PIL package.")



def _screenshot(viewport=None):
    """ Take a screenshot using glReadPixels. Not sure where to put this 
    yet, so a private function for now. Used in make.py.
    """
    import numpy as np
    from vispy.gloo import gl
    #gl.glReadBuffer(gl.GL_BACK)  Not avaliable in ES 2.0
    if viewport is None:
        viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)
    x,y,w,h = viewport
    gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)  # PACK, not UNPACK
    im = gl.glReadPixels(x, y, w, h, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
    gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 4)
    # reshape, flip, and return
    if not isinstance(im, np.ndarray):
        im = np.frombuffer(im, np.uint8)
    im.shape = h,w,3
    im = np.flipud(im)
    return im
