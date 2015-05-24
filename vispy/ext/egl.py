# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" A ctypes-based API to EGL.
"""

import os
import ctypes
from ctypes import c_int as _c_int, POINTER as _POINTER, c_void_p, c_char_p

_egl_file = None
if 'EGL_LIBRARY' in os.environ:
    if os.path.exists(os.environ['EGL_LIBRARY']):
        _egl_file = os.path.realpath(os.environ['EGL_LIBRARY'])

# Else, try to find it
if _egl_file is None:
    _egl_file = ctypes.util.find_library('EGL')

# Else, we failed and exit
if _egl_file is None:
    raise OSError('EGL library not found')

# Load it
_lib = ctypes.CDLL(_egl_file)


## Constants

EGL_FALSE = 0
EGL_TRUE = 1

# Out-of-band handle values
EGL_DEFAULT_DISPLAY = 0
EGL_NO_CONTEXT = 0
EGL_NO_DISPLAY = 0
EGL_NO_SURFACE = 0

# Out-of-band attribute value
EGL_DONT_CARE = -1

# Errors / GetError return values
EGL_SUCCESS = 0x3000
EGL_NOT_INITIALIZED = 0x3001
EGL_BAD_ACCESS = 0x3002
EGL_BAD_ALLOC = 0x3003
EGL_BAD_ATTRIBUTE = 0x3004
EGL_BAD_CONFIG = 0x3005
EGL_BAD_CONTEXT = 0x3006
EGL_BAD_CURRENT_SURFACE = 0x3007
EGL_BAD_DISPLAY = 0x3008
EGL_BAD_MATCH = 0x3009
EGL_BAD_NATIVE_PIXMAP = 0x300A
EGL_BAD_NATIVE_WINDOW = 0x300B
EGL_BAD_PARAMETER = 0x300C
EGL_BAD_SURFACE = 0x300D
EGL_CONTEXT_LOST = 0x300E  # EGL 1.1 - IMG_power_management

# Reserved 0x300F-0x301F for additional errors

# Config attributes
EGL_BUFFER_SIZE = 0x3020
EGL_ALPHA_SIZE = 0x3021
EGL_BLUE_SIZE = 0x3022
EGL_GREEN_SIZE = 0x3023
EGL_RED_SIZE = 0x3024
EGL_DEPTH_SIZE = 0x3025
EGL_STENCIL_SIZE = 0x3026
EGL_CONFIG_CAVEAT = 0x3027
EGL_CONFIG_ID = 0x3028
EGL_LEVEL = 0x3029
EGL_MAX_PBUFFER_HEIGHT = 0x302A
EGL_MAX_PBUFFER_PIXELS = 0x302B
EGL_MAX_PBUFFER_WIDTH = 0x302C
EGL_NATIVE_RENDERABLE = 0x302D
EGL_NATIVE_VISUAL_ID = 0x302E
EGL_NATIVE_VISUAL_TYPE = 0x302F
EGL_SAMPLES = 0x3031
EGL_SAMPLE_BUFFERS = 0x3032
EGL_SURFACE_TYPE = 0x3033
EGL_TRANSPARENT_TYPE = 0x3034
EGL_TRANSPARENT_BLUE_VALUE = 0x3035
EGL_TRANSPARENT_GREEN_VALUE = 0x3036
EGL_TRANSPARENT_RED_VALUE = 0x3037
EGL_NONE = 0x3038  # Attrib list terminator
EGL_BIND_TO_TEXTURE_RGB = 0x3039
EGL_BIND_TO_TEXTURE_RGBA = 0x303A
EGL_MIN_SWAP_INTERVAL = 0x303B
EGL_MAX_SWAP_INTERVAL = 0x303C
EGL_LUMINANCE_SIZE = 0x303D
EGL_ALPHA_MASK_SIZE = 0x303E
EGL_COLOR_BUFFER_TYPE = 0x303F
EGL_RENDERABLE_TYPE = 0x3040
EGL_MATCH_NATIVE_PIXMAP = 0x3041  # Pseudo-attribute (not queryable)
EGL_CONFORMANT = 0x3042

# Reserved 0x3041-0x304F for additional config attributes

# Config attribute values
EGL_SLOW_CONFIG = 0x3050  # EGL_CONFIG_CAVEAT value
EGL_NON_CONFORMANT_CONFIG = 0x3051  # EGL_CONFIG_CAVEAT value
EGL_TRANSPARENT_RGB = 0x3052  # EGL_TRANSPARENT_TYPE value
EGL_RGB_BUFFER = 0x308E  # EGL_COLOR_BUFFER_TYPE value
EGL_LUMINANCE_BUFFER = 0x308F  # EGL_COLOR_BUFFER_TYPE value

# More config attribute values, for EGL_TEXTURE_FORMAT
EGL_NO_TEXTURE = 0x305C
EGL_TEXTURE_RGB = 0x305D
EGL_TEXTURE_RGBA = 0x305E
EGL_TEXTURE_2D = 0x305F

# Config attribute mask bits
EGL_PBUFFER_BIT = 0x0001  # EGL_SURFACE_TYPE mask bits
EGL_PIXMAP_BIT = 0x0002  # EGL_SURFACE_TYPE mask bits
EGL_WINDOW_BIT = 0x0004  # EGL_SURFACE_TYPE mask bits
EGL_VG_COLORSPACE_LINEAR_BIT = 0x0020  # EGL_SURFACE_TYPE mask bits
EGL_VG_ALPHA_FORMAT_PRE_BIT = 0x0040  # EGL_SURFACE_TYPE mask bits
EGL_MULTISAMPLE_RESOLVE_BOX_BIT = 0x0200  # EGL_SURFACE_TYPE mask bits
EGL_SWAP_BEHAVIOR_PRESERVED_BIT = 0x0400  # EGL_SURFACE_TYPE mask bits

EGL_OPENGL_ES_BIT = 0x0001  # EGL_RENDERABLE_TYPE mask bits
EGL_OPENVG_BIT = 0x0002  # EGL_RENDERABLE_TYPE mask bits
EGL_OPENGL_ES2_BIT = 0x0004  # EGL_RENDERABLE_TYPE mask bits
EGL_OPENGL_BIT = 0x0008  # EGL_RENDERABLE_TYPE mask bits

# QueryString targets
EGL_VENDOR = 0x3053
EGL_VERSION = 0x3054
EGL_EXTENSIONS = 0x3055
EGL_CLIENT_APIS = 0x308D

# QuerySurface / SurfaceAttrib / CreatePbufferSurface targets
EGL_HEIGHT = 0x3056
EGL_WIDTH = 0x3057
EGL_LARGEST_PBUFFER = 0x3058
EGL_TEXTURE_FORMAT = 0x3080
EGL_TEXTURE_TARGET = 0x3081
EGL_MIPMAP_TEXTURE = 0x3082
EGL_MIPMAP_LEVEL = 0x3083
EGL_RENDER_BUFFER = 0x3086
EGL_VG_COLORSPACE = 0x3087
EGL_VG_ALPHA_FORMAT = 0x3088
EGL_HORIZONTAL_RESOLUTION = 0x3090
EGL_VERTICAL_RESOLUTION = 0x3091
EGL_PIXEL_ASPECT_RATIO = 0x3092
EGL_SWAP_BEHAVIOR = 0x3093
EGL_MULTISAMPLE_RESOLVE = 0x3099

# EGL_RENDER_BUFFER values / BindTexImage / ReleaseTexImage buffer targets
EGL_BACK_BUFFER = 0x3084
EGL_SINGLE_BUFFER = 0x3085

# OpenVG color spaces
EGL_VG_COLORSPACE_sRGB = 0x3089  # EGL_VG_COLORSPACE value
EGL_VG_COLORSPACE_LINEAR = 0x308A  # EGL_VG_COLORSPACE value

# OpenVG alpha formats
EGL_VG_ALPHA_FORMAT_NONPRE = 0x308B  # EGL_ALPHA_FORMAT value
EGL_VG_ALPHA_FORMAT_PRE = 0x308C  # EGL_ALPHA_FORMAT value

# Constant scale factor by which fractional display resolutions &
# * aspect ratio are scaled when queried as integer values.

EGL_DISPLAY_SCALING = 10000

# Unknown display resolution/aspect ratio
EGL_UNKNOWN = -1

# Back buffer swap behaviors
EGL_BUFFER_PRESERVED = 0x3094  # EGL_SWAP_BEHAVIOR value
EGL_BUFFER_DESTROYED = 0x3095  # EGL_SWAP_BEHAVIOR value

# CreatePbufferFromClientBuffer buffer types
EGL_OPENVG_IMAGE = 0x3096

# QueryContext targets
EGL_CONTEXT_CLIENT_TYPE = 0x3097

# CreateContext attributes
EGL_CONTEXT_CLIENT_VERSION = 0x3098

# Multisample resolution behaviors
EGL_MULTISAMPLE_RESOLVE_DEFAULT = 0x309A  # EGL_MULTISAMPLE_RESOLVE value
EGL_MULTISAMPLE_RESOLVE_BOX = 0x309B  # EGL_MULTISAMPLE_RESOLVE value

# BindAPI/QueryAPI targets
EGL_OPENGL_ES_API = 0x30A0
EGL_OPENVG_API = 0x30A1
EGL_OPENGL_API = 0x30A2

# GetCurrentSurface targets
EGL_DRAW = 0x3059
EGL_READ = 0x305A

# WaitNative engines
EGL_CORE_NATIVE_ENGINE = 0x305B

# EGL 1.2 tokens renamed for consistency in EGL 1.3
EGL_COLORSPACE = EGL_VG_COLORSPACE
EGL_ALPHA_FORMAT = EGL_VG_ALPHA_FORMAT
EGL_COLORSPACE_sRGB = EGL_VG_COLORSPACE_sRGB
EGL_COLORSPACE_LINEAR = EGL_VG_COLORSPACE_LINEAR
EGL_ALPHA_FORMAT_NONPRE = EGL_VG_ALPHA_FORMAT_NONPRE
EGL_ALPHA_FORMAT_PRE = EGL_VG_ALPHA_FORMAT_PRE


## The functions

_lib.eglGetDisplay.argtypes = _c_int,
_lib.eglGetDisplay.restype = _c_int
_lib.eglInitialize.argtypes = c_void_p, _POINTER(_c_int), _POINTER(_c_int)
_lib.eglTerminate.argtypes = c_void_p,
_lib.eglChooseConfig.argtypes = (c_void_p, _POINTER(_c_int),
                                 _POINTER(c_void_p), _c_int, _POINTER(_c_int))
_lib.eglCreateWindowSurface.argtypes = (c_void_p, c_void_p,
                                        c_void_p, _POINTER(_c_int))
_lib.eglCreatePbufferSurface.argtypes = (c_void_p, c_void_p, _POINTER(_c_int))
_lib.eglCreateContext.argtypes = c_void_p, c_void_p, c_void_p, _POINTER(_c_int)
_lib.eglMakeCurrent.argtypes = (c_void_p,) * 4
_lib.eglSwapBuffers.argtypes = (c_void_p,) * 2
_lib.eglDestroySurface.argtypes = (c_void_p,) * 2
_lib.eglQueryString.argtypes = (c_void_p, _c_int)
_lib.eglQueryString.restype = c_char_p


def eglGetError():
    """ Check for errors, returns an enum (int).
    """
    return _lib.eglGetError()


def eglGetDisplay(display=EGL_DEFAULT_DISPLAY):
    """ Connect to the EGL display server.
    """
    res = _lib.eglGetDisplay(display)
    if not res or res == EGL_NO_DISPLAY:
        raise RuntimeError('Could not create display')
    return res


def eglInitialize(display):
    """ Initialize EGL and return EGL version tuple.
    """
    majorVersion = (_c_int*1)()
    minorVersion = (_c_int*1)()
    res = _lib.eglInitialize(display, majorVersion, minorVersion)
    if res == EGL_FALSE:
        raise RuntimeError('Could not initialize')
    return majorVersion[0], minorVersion[0]


def eglTerminate(display):
    """ Initialize EGL and return EGL version tuple.
    """
    _lib.eglTerminate(display)


def eglQueryString(display, name):
    """ Query string from display
    """
    out = _lib.eglQueryString(display, name)
    if not out:
        raise RuntimeError('Could not query %s' % name)
    return out


DEFAULT_ATTRIB_LIST = (EGL_RED_SIZE, 8, EGL_BLUE_SIZE, 8,
                       EGL_GREEN_SIZE, 8, EGL_ALPHA_SIZE, 8,
                       EGL_BIND_TO_TEXTURE_RGBA, EGL_TRUE,
                       EGL_COLOR_BUFFER_TYPE, EGL_RGB_BUFFER,
                       EGL_CONFORMANT, EGL_OPENGL_ES2_BIT,
                       EGL_RENDERABLE_TYPE, EGL_OPENGL_ES2_BIT,
                       EGL_NATIVE_RENDERABLE, EGL_TRUE,
                       EGL_SURFACE_TYPE, EGL_PBUFFER_BIT)


def _convert_attrib_list(attribList):
    attribList = attribList or []
    attribList = [a for a in attribList] + [EGL_NONE]
    attribList = (_c_int*len(attribList))(*attribList)
    return attribList


def eglChooseConfig(display, attribList=DEFAULT_ATTRIB_LIST):
    attribList = _convert_attrib_list(attribList)
    numConfigs = (_c_int*1)()
    _lib.eglChooseConfig(display, attribList, None, 0, numConfigs)
    n = numConfigs[0]
    if n <= 0:
        raise RuntimeError('Could not find any suitable config.')
    config = (c_void_p*n)()
    _lib.eglChooseConfig(display, attribList, config, n, numConfigs)
    return config


def _check_res(res):
    if res == EGL_NO_SURFACE:
        e = eglGetError()
    else:
        return res
    if e == EGL_BAD_MATCH:
        raise ValueError('Cannot create surface: attributes do not match ' +
                         'or given config cannot render in window.')
    elif e == EGL_BAD_CONFIG:
        raise ValueError('Cannot create surface: given config is not ' +
                         'supported by this system.')
    elif e == EGL_BAD_NATIVE_WINDOW:
        raise ValueError('Cannot create surface: the given native window ' +
                         'handle is invalid.')
    elif e == EGL_BAD_ALLOC:
        raise RuntimeError('Could not allocate surface: not enough ' +
                           'resources or native window already associated ' +
                           'with another config.')
    else:
        raise RuntimeError('Could not create window surface due to ' +
                           'unknown error: %i' % e)


def eglCreateWindowSurface(display, config, window, attribList=None):
    # Deal with attrib list
    attribList = _convert_attrib_list(attribList)
    return _check_res(_lib.eglCreateWindowSurface(display, config,
                                                  window, attribList))


def eglCreatePbufferSurface(display, config, attribList=None):
    # Deal with attrib list
    attribList = _convert_attrib_list(attribList)
    #
    return _check_res(_lib.eglCreatePbufferSurface(display, config,
                                                   attribList))


def eglCreateContext(display, config, shareContext=EGL_NO_CONTEXT,
                     attribList=None):
    # Deal with attrib list
    attribList = attribList or [EGL_CONTEXT_CLIENT_VERSION, 2]
    attribList = [a for a in attribList] + [EGL_NONE]
    attribList = (_c_int*len(attribList))(*attribList)
    #
    res = _lib.eglCreateContext(display, config, shareContext, attribList)
    if res == EGL_NO_CONTEXT:
        e = eglGetError()
        if e == EGL_BAD_CONFIG:
            raise ValueError('Could not create context: given config is ' +
                             'not supported by this system.')
        else:
            raise RuntimeError('Could not create context due to ' +
                               'unknown error: %i' % e)
    return res


def eglMakeCurrent(display, draw, read, context):
    res = _lib.eglMakeCurrent(display, draw, read, context)
    if res == EGL_FALSE:
        raise RuntimeError('Could not make the context current.')


def eglSwapBuffers(display, surface):
    res = _lib.eglSwapBuffers(display, surface)
    if res == EGL_FALSE:
        raise RuntimeError('Could not swap buffers.')


def eglDestroySurface(display, surface):
    res = _lib.eglDestroySurface(display, surface)
    if res == EGL_FALSE:
        raise RuntimeError('Could not destroy surface')
