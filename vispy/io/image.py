# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author: Luke Campagnola
# -----------------------------------------------------------------------------


import struct
import zlib
import numpy as np


def make_png(data, level=6):
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
