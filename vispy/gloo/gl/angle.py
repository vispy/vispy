# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" GL ES 2.0 API implemented via Angle (i.e translated to DirectX).
"""

import ctypes

from . import _copy_gl_functions
from ._constants import *  # noqa


## Ctypes stuff

# todo: were are we going to put our libs?
dirname = r'C:\Users\Almar\AppData\Local\Chromium\Application\34.0.1790.0'

# Load dependency (so that libGLESv2 can find it
fname = dirname + r'\d3dcompiler_46.dll'
_libdum = ctypes.windll.LoadLibrary(fname)

# Load GL ES 2.0 lib (Angle)
fname = dirname + r'\libGLESv2.dll'
_lib = ctypes.windll.LoadLibrary(fname)


## Compatibility


def glShaderSource_compat(handle, code):
    """ Easy for real ES 2.0.
    """
    glShaderSource(handle, [code])
    return []


## Inject


from . import _angle
_copy_gl_functions(_angle, globals())
