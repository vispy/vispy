# -*- coding: utf-8 -*-
# vispy: testskip
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""A ctypes-based API to OSMesa"""
from __future__ import print_function
import os
import ctypes
import ctypes.util
from ctypes import c_int as _c_int, c_uint as _c_uint, c_void_p

# See vispy/gloo/gl/_constants.py for reference
GL_RGBA = 6408
GL_UNSIGNED_BYTE = 5121
GL_VERSION = 7938

_osmesa_file = None
if 'OSMESA_LIBRARY' in os.environ:
    if os.path.exists(os.environ['OSMESA_LIBRARY']):
        _osmesa_file = os.path.realpath(os.environ['OSMESA_LIBRARY'])

# Else, try to find it
if _osmesa_file is None:
    _osmesa_file = ctypes.util.find_library('OSMesa')

# Else, we failed and exit
if _osmesa_file is None:
    raise OSError('OSMesa library not found')

# Load it
_lib = ctypes.CDLL(_osmesa_file)

# Constants
OSMESA_RGBA = GL_RGBA

# Functions

# GLAPI OSMesaContext GLAPIENTRY
# OSMesaCreateContext( GLenum format, OSMesaContext sharelist );
_lib.OSMesaCreateContext.argtypes = _c_int, c_void_p
_lib.OSMesaCreateContext.restype = c_void_p
# GLAPI void GLAPIENTRY
# OSMesaDestroyContext( OSMesaContext ctx );
_lib.OSMesaDestroyContext.argtypes = c_void_p,
# GLAPI GLboolean GLAPIENTRY
# OSMesaMakeCurrent( OSMesaContext ctx, void *buffer, GLenum type,
#                   GLsizei width, GLsizei height );
_lib.OSMesaMakeCurrent.argtypes = c_void_p, c_void_p, _c_int, _c_int, _c_int
_lib.OSMesaMakeCurrent.restype = _c_int
# GLAPI OSMesaContext GLAPIENTRY
# OSMesaGetCurrentContext( void );
_lib.OSMesaGetCurrentContext.restype = c_void_p


def allocate_pixels_buffer(width, height):
    """Helper function to allocate a buffer to contain an image of
    width * height suitable for OSMesaMakeCurrent
    """
    # Seems like OSMesa has some trouble with non-RGBA buffers, so enforce
    # RGBA
    return (_c_uint * width * height * 4)()


def OSMesaCreateContext():
    return ctypes.cast(_lib.OSMesaCreateContext(OSMESA_RGBA, None), c_void_p)


def OSMesaDestroyContext(context):
    _lib.OSMesaDestroyContext(context)


def OSMesaMakeCurrent(context, buffer, width, height):
    ret = _lib.OSMesaMakeCurrent(context, buffer, GL_UNSIGNED_BYTE,
                                 width, height)
    return ret != 0


def OSMesaGetCurrentContext():
    return c_void_p(_lib.OSMesaGetCurrentContext())

if __name__ == '__main__':
    """This test basic OSMesa functionality"""
    # If you have OSMesa installed alongside normal OpenGL, execute with
    # VISPY_GL_LIB=/opt/osmesa_llvmpipe/lib/libGLESv2.so \
    #   LD_LIBRARY_PATH=/opt/osmesa_llvmpipe/lib/ \
    #   OSMESA_LIBRARY=/opt/osmesa_llvmpipe/lib/libOSMesa.so \
    #   python vispy/ext/osmesa.py
    context = OSMesaCreateContext()
    w, h = 640, 480
    pixels = allocate_pixels_buffer(w, h)
    ok = OSMesaMakeCurrent(context, pixels, 640, 480)
    if not ok:
        raise RuntimeError('Failed OSMesaMakeCurrent')
    if not (OSMesaGetCurrentContext().value == context.value):
        raise RuntimeError('OSMesa context not correctly attached')

    _lib.glGetString.argtypes = (ctypes.c_uint,)
    _lib.glGetString.restype = ctypes.c_char_p

    print("OpenGL version : ", _lib.glGetString(GL_VERSION))

    OSMesaDestroyContext(context)
    if OSMesaGetCurrentContext().value is not None:
        raise RuntimeError('Failed to destroy OSMesa context')
