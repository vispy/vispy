# -*- coding: utf-8 -*-
import numpy as np

from . import gl


def _screenshot(viewport=None):
    """ Take a screenshot using glReadPixels. Not sure where to put this
    yet, so a private function for now. Used in make.py.
    """
    # gl.glReadBuffer(gl.GL_BACK)  Not avaliable in ES 2.0
    if viewport is None:
        viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)
    x, y, w, h = viewport
    gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)  # PACK, not UNPACK
    im = gl.glReadPixels(x, y, w, h, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
    gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 4)
    # reshape, flip, and return
    if not isinstance(im, np.ndarray):
        im = np.frombuffer(im, np.uint8)
    im.shape = h, w, 3
    im = np.flipud(im)
    return im
