# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" GL ES 2.0 API implemented via desktop GL (i.e subset of normal OpenGL).
"""

import sys
import ctypes.util

from . import _copy_gl_functions
from ._constants import *  # noqa

## Ctypes stuff


# Load the OpenGL library. We more or less follow the same approach
# as PyOpenGL does internally

if sys.platform.startswith('win'):
    # Windows
    _lib = ctypes.windll.opengl32
    try:
        wglGetProcAddress = _lib.wglGetProcAddress
        wglGetProcAddress.restype = ctypes.CFUNCTYPE(
            ctypes.POINTER(ctypes.c_int))
        wglGetProcAddress.argtypes = [ctypes.c_char_p]
        _have_get_proc_address = True
    except AttributeError:
        _have_get_proc_address = False
else:
    # Unix-ish
    _have_get_proc_address = False
    # Get filename
    if sys.platform.startswith('darwin'):
        _fname = ctypes.util.find_library('OpenGL')
    else:
        _fname = ctypes.util.find_library('GL')
    if not _fname:
        raise RuntimeError('Could not load OpenGL library.')
    # Load lib
    _lib = ctypes.cdll.LoadLibrary(_fname)


def _have_context():
    return _lib.glGetError() != 1282  # GL_INVALID_OPERATION


def _get_gl_func(name, restype, argtypes):
    # Based on a function in Pyglet
    try:
        # Try using normal ctypes stuff
        func = getattr(_lib, name)
        func.restype = restype
        func.argtypes = argtypes
        return func
    except AttributeError:
        if sys.platform.startswith('win'):
            # Ask for a pointer to the function, this is the approach
            # for OpenGL extensions on Windows
            fargs = (restype,) + argtypes
            ftype = ctypes.WINFUNCTYPE(*fargs)
            if not _have_get_proc_address:
                raise RuntimeError('Function %s not available.' % name)
            if not _have_context():
                raise RuntimeError('Using %s with no OpenGL context.' % name)
            address = wglGetProcAddress(name.encode('utf-8'))
            if address:
                return ctypes.cast(address, ftype)
        # If not Windows or if we did not return function object on Windows:
        raise RuntimeError('Function %s not present in context.' % name)


## Compatibility


def glShaderSource_compat(handle, code):
    """ This version of glShaderSource applies small modifications
    to the given GLSL code in order to make it more compatible between
    desktop and ES2.0 implementations. Specifically:
      * It sets the #version pragma (if none is given already)
      * It returns a (possibly empty) set of enums that should be enabled
        (for automatically enabling point sprites)
    """

    # Make a string
    if isinstance(code, (list, tuple)):
        code = '\n'.join(code)

    # Determine whether this is a vertex or fragment shader
    code_ = '\n' + code
    is_vertex = '\nattribute' in code_
    is_fragment = not is_vertex

    # Determine whether to write the #version pragma
    write_version = True
    for line in code.splitlines():
        if line.startswith('#version'):
            write_version = False
            logger.warning('For compatibility accross different GL backends, '
                           'avoid using the #version pragma.')
    if write_version:
        code = '#version 120\n#line 0\n' + code

    # Do the call
    glShaderSource(handle, [code])

    # Determine whether to activate point sprites
    enums = set()
    if is_fragment and 'gl_PointCoord' in code:
        enums.add(Enum('GL_VERTEX_PROGRAM_POINT_SIZE', 34370))
        enums.add(Enum('GL_POINT_SPRITE', 34913))
    return enums
    return []


## Inject


from . import _desktop
_copy_gl_functions(_desktop, globals())
