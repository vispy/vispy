# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" GL ES 2.0 API implemented via desktop GL (i.e subset of normal OpenGL).
"""

import os
import sys
import ctypes.util

from . import _copy_gl_functions
from ._constants import *  # noqa
from ...util import logger

# Ctypes stuff


# Load the OpenGL library. We more or less follow the same approach
# as PyOpenGL does internally

_have_get_proc_address = False
_lib = os.getenv('VISPY_GL_LIB', '')
if _lib != '':
    if sys.platform.startswith('win'):
        _lib = ctypes.windll.LoadLibrary(_lib)
    else:
        _lib = ctypes.cdll.LoadLibrary(_lib)
elif sys.platform.startswith('win'):
    # Windows
    _lib = ctypes.windll.opengl32
    try:
        wglGetProcAddress = _lib.wglGetProcAddress
        wglGetProcAddress.restype = ctypes.CFUNCTYPE(
            ctypes.POINTER(ctypes.c_int))
        wglGetProcAddress.argtypes = [ctypes.c_char_p]
        _have_get_proc_address = True
    except AttributeError:
        pass
else:
    # Unix-ish
    if sys.platform.startswith('darwin'):
        _fname = ctypes.util.find_library('OpenGL')
    else:
        _fname = ctypes.util.find_library('GL')
    if not _fname:
        logger.warning('Could not load OpenGL library.')
        _lib = None
    else:
        # Load lib
        _lib = ctypes.cdll.LoadLibrary(_fname)


def _have_context():
    return _lib.glGetError() != 1282  # GL_INVALID_OPERATION


def _get_gl_version(_lib):
    """Helper to get the GL version string"""
    try:
        return _lib.glGetString(7938).decode('utf-8')
    except Exception:
        return 'unknown'


def _get_gl_func(name, restype, argtypes):
    # Based on a function in Pyglet
    if _lib is None:
        raise RuntimeError('Could not load OpenGL library, gl cannot be used')
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
                raise RuntimeError('Function %s not available '
                                   '(OpenGL version is %s).'
                                   % (name, _get_gl_version(_lib)))
            if not _have_context():
                raise RuntimeError('Using %s with no OpenGL context.' % name)
            address = wglGetProcAddress(name.encode('utf-8'))
            if address:
                return ctypes.cast(address, ftype)
        # If not Windows or if we did not return function object on Windows:
        raise RuntimeError('Function %s not present in context '
                           '(OpenGL version is %s).'
                           % (name, _get_gl_version(_lib)))


# Inject

from . import _gl2  # noqa
_copy_gl_functions(_gl2, globals())
