# -*- coding: utf-8 -*-
# vispy: testskip
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""A ctypes-based API to OSMesa
"""

import os
import ctypes
from ctypes import c_int as _c_int, c_uint as _c_uint, POINTER as _POINTER, \
                   c_void_p, c_char_p

from vispy.gloo import gl

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

## Constants
OSMESA_RGBA = gl.GL_RGBA

## Functions

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
    width * height suitable for OSMesaMakeCurrent"""
    # Seems like OSMesa has some trouble with non-RGBA buffers, so enforce
    # RGBA
    return (_c_uint * width * height * 4)()

def OSMesaCreateContext():
    return ctypes.cast(_lib.OSMesaCreateContext(OSMESA_RGBA, None), c_void_p)

def OSMesaDestroyContext(context):
    _lib.OSMesaDestroyContext(context)

def OSMesaMakeCurrent(context, buffer, width, height):
    ret = _lib.OSMesaMakeCurrent(context, buffer, gl.GL_UNSIGNED_BYTE,
                                 width, height)
    return ret != 0

def OSMesaGetCurrentContext():
    return c_void_p(_lib.OSMesaGetCurrentContext())

if __name__ == '__main__':
    """This test basic functionality"""
    # Execute with
    # VISPY_GL_LIB=/opt/osmesa_llvmpipe/lib/libGLESv2.so \
    #   LD_LIBRARY_PATH=/opt/osmesa_llvmpipe/lib/ \
    #   OSMESA_LIBRARY=/opt/osmesa_llvmpipe/lib/libOSMesa.so \
    #   python vispy/ext/osmesa.py
    context = OSMesaCreateContext()
    w, h = 640, 480
    pixels = allocate_pixels_buffer(w, h)
    ok = OSMesaMakeCurrent(context, pixels, 640, 480)
    assert ok == True, 'Failed to OSMesaMakeCurrent'
    assert OSMesaGetCurrentContext().value == context.value

    OSMesaDestroyContext(context)
    assert OSMesaGetCurrentContext().value == None
