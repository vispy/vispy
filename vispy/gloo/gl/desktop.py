# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" vispy.gloo.gl.desktop: namespace for OpenGL ES 2.0 API based on the
desktop OpenGL implementation.
"""

from __future__ import division

import sys
import ctypes
from OpenGL import GL as _GL
import OpenGL.GL.framebufferobjects as FBO

from . import _GL_ENUM
from . import _desktop, _desktop_ext
from ...util import logger

# Prepare namespace with constants and ext
from ._constants import *  # noqa
ext = _desktop_ext


def _make_unavailable_func(funcname):
    def cb(*args, **kwds):
        raise RuntimeError('OpenGL API call "%s" is not available.' % funcname)
    return cb


def _get_function_from_pyopengl(funcname):
    """ Try getting the given function from PyOpenGL, return
    a dummy function (that shows a warning when called) if it
    could not be found.
    """
    func = None
    # Get function from GL
    try:
        func = getattr(_GL, funcname)
    except AttributeError:
        # Get function from FBO

        try:
            func = getattr(FBO, funcname)
        except AttributeError:
            # Some functions are known by a slightly different name
            # e.g. glDepthRangef, glDepthRangef
            if funcname.endswith('f'):
                try:
                    func = getattr(_GL, funcname[:-1])
                except AttributeError:
                    pass

    # Set dummy function if we could not find it
    if func is None:
        func = _make_unavailable_func(funcname)
        logger.warn('warning: %s not available' % funcname)
    return func


def _inject():
    """ Get GL functions from pyopengl. Inject in *this* namespace
    and the ext namespace.
    Note the similatity with vispy.gloo.gl.use().
    """

    # Import functions here
    NS = globals()
    funcnames = _desktop._glfunctions
    for name in funcnames:
        func = _get_function_from_pyopengl(name)
        NS[name] = func

    # Import functions in ext
    NS = ext.__dict__
    funcnames = _desktop_ext._glfunctions
    for name in funcnames:
        func = _get_function_from_pyopengl(name)
        NS[name] = func


def _fix():
    """ Apply some fixes and patches.
    """
    NS = globals()
    # Fix glGetActiveAttrib, since if its just the ctypes function
    if ('glGetActiveAttrib' in NS and
            hasattr(NS['glGetActiveAttrib'], 'restype')):

        def new_glGetActiveAttrib(program, index):
            # Prepare
            bufsize = 32
            length = ctypes.c_int()
            size = ctypes.c_int()
            type = ctypes.c_int()
            name = ctypes.create_string_buffer(bufsize)
            # Call
            _GL.glGetActiveAttrib(
                program,
                index,
                bufsize,
                ctypes.byref(length),
                ctypes.byref(size),
                ctypes.byref(type),
                name)
            # Return Python objects
            # return name.value.decode('utf-8'), size.value, type.value
            return name.value, size.value, type.value

        # Patch
        NS['glGetActiveAttrib'] = new_glGetActiveAttrib

    # Monkey-patch pyopengl to fix a bug in glBufferSubData
    if sys.version_info > (3,):
        buffersubdatafunc = NS['glBufferSubData']
        if hasattr(buffersubdatafunc, 'wrapperFunction'):
            buffersubdatafunc = buffersubdatafunc.wrapperFunction
        _m = sys.modules[buffersubdatafunc.__module__]
        _m.long = int


# Apply
_inject()
_fix()


# Compatibility functions


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
            logger.warn('For compatibility accross different GL backends, ' +
                        'avoid using the #version pragma.')
    if write_version:
        code = '#version 120\n#line 0\n' + code

    # Do the call
    glShaderSource(handle, [code])

    # Determine whether to activate point sprites
    enums = set()
    if is_fragment and 'gl_PointCoord' in code:
        enums.add(_GL_ENUM('GL_VERTEX_PROGRAM_POINT_SIZE', 34370))
        enums.add(_GL_ENUM('GL_POINT_SPRITE', 34913))
    return enums
