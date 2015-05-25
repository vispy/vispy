# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Luke Campagnola
# -----------------------------------------------------------------------------


import struct
import zlib
import numpy as np

from ..ext.png import Reader


def _make_png(data, level=6):
    """Convert numpy array to PNG byte array.

    Parameters
    ----------
    data : numpy.ndarray
        Data must be (H, W, 3 | 4) with dtype = np.ubyte (np.uint8)
    level : int
        https://docs.python.org/2/library/zlib.html#zlib.compress
        An integer from 0 to 9 controlling the level of compression:

            * 1 is fastest and produces the least compression,
            * 9 is slowest and produces the most.
            * 0 is no compression.

        The default value is 6.

    Returns
    -------
    png : array
        PNG formatted array
    """
    # Eventually we might want to use ext/png.py for this, but this
    # routine *should* be faster b/c it's speacialized for our use case

    def mkchunk(data, name):
        if isinstance(data, np.ndarray):
            size = data.nbytes
        else:
            size = len(data)
        chunk = np.empty(size + 12, dtype=np.ubyte)
        chunk.data[0:4] = np.array(size, '>u4').tostring()
        chunk.data[4:8] = name.encode('ASCII')
        chunk.data[8:8 + size] = data
        # and-ing may not be necessary, but is done for safety:
        # https://docs.python.org/3/library/zlib.html#zlib.crc32
        chunk.data[-4:] = np.array(zlib.crc32(chunk[4:-4]) & 0xffffffff,
                                   '>u4').tostring()
        return chunk

    if data.dtype != np.ubyte:
        raise TypeError('data.dtype must be np.ubyte (np.uint8)')

    dim = data.shape[2]  # Dimension
    if dim not in (3, 4):
        raise TypeError('data.shape[2] must be in (3, 4)')

    # www.libpng.org/pub/png/spec/1.2/PNG-Chunks.html#C.IHDR
    if dim == 4:
        ctyp = 0b0110  # RGBA
    else:
        ctyp = 0b0010  # RGB

    # www.libpng.org/pub/png/spec/1.2/PNG-Structure.html
    header = b'\x89PNG\x0d\x0a\x1a\x0a'  # header

    h, w = data.shape[:2]
    depth = data.itemsize * 8
    ihdr = struct.pack('!IIBBBBB', w, h, depth, ctyp, 0, 0, 0)
    c1 = mkchunk(ihdr, 'IHDR')

    # www.libpng.org/pub/png/spec/1.2/PNG-Chunks.html#C.IDAT
    # insert filter byte at each scanline
    idat = np.empty((h, w * dim + 1), dtype=np.ubyte)
    idat[:, 1:] = data.reshape(h, w * dim)
    idat[:, 0] = 0

    comp_data = zlib.compress(idat, level)
    c2 = mkchunk(comp_data, 'IDAT')
    c3 = mkchunk(np.empty((0,), dtype=np.ubyte), 'IEND')

    # concatenate
    lh = len(header)
    png = np.empty(lh + c1.nbytes + c2.nbytes + c3.nbytes, dtype=np.ubyte)
    png.data[:lh] = header
    p = lh

    for chunk in (c1, c2, c3):
        png[p:p + len(chunk)] = chunk
        p += chunk.nbytes

    return png


def read_png(filename):
    """Read a PNG file to RGB8 or RGBA8

    Unlike imread, this requires no external dependencies.

    Parameters
    ----------
    filename : str
        File to read.

    Returns
    -------
    data : array
        Image data.

    See also
    --------
    write_png, imread, imsave
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


def write_png(filename, data):
    """Write a PNG file

    Unlike imsave, this requires no external dependencies.

    Parameters
    ----------
    filename : str
        File to save to.
    data : array
        Image data.

    See also
    --------
    read_png, imread, imsave
    """
    data = np.asarray(data)
    if not data.ndim == 3 and data.shape[-1] in (3, 4):
        raise ValueError('data must be a 3D array with last dimension 3 or 4')
    with open(filename, 'wb') as f:
        f.write(_make_png(data))  # Save array with make_png


def imread(filename, format=None):
    """Read image data from disk

    Requires imageio or PIL.

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

    See also
    --------
    imsave, read_png, write_png
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
    """Save image data to disk

    Requires imageio or PIL.

    Parameters
    ----------
    filename : str
        Filename to write.
    im : array
        Image data.
    format : str | None
        Format of the file. If None, it will be inferred from the filename.

    See also
    --------
    imread, read_png, write_png
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
