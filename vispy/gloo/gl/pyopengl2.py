# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""GL ES 2.0 API implemented via pyOpenGL library. Intended as a
fallback and for testing.
"""

from OpenGL import GL as _GL
import OpenGL.GL.framebufferobjects as _FBO

from ...util import logger

from . import _copy_gl_functions
from ._constants import *  # noqa


def _patch():
    """Monkey-patch pyopengl to fix a bug in glBufferSubData."""
    import sys
    from OpenGL import GL
    if sys.version_info > (3,):
        buffersubdatafunc = GL.glBufferSubData
        if hasattr(buffersubdatafunc, 'wrapperFunction'):
            buffersubdatafunc = buffersubdatafunc.wrapperFunction
        _m = sys.modules[buffersubdatafunc.__module__]
        _m.long = int

    # Fix missing enum
    try:
        from OpenGL.GL.VERSION import GL_2_0
        GL_2_0.GL_OBJECT_SHADER_SOURCE_LENGTH = GL_2_0.GL_SHADER_SOURCE_LENGTH
    except Exception:
        pass

# Patch OpenGL package
_patch()


# Inject

def _make_unavailable_func(funcname):
    def cb(*args, **kwargs):
        raise RuntimeError('OpenGL API call "%s" is not available.' % funcname)
    return cb


def _get_function_from_pyopengl(funcname):
    """Try getting the given function from PyOpenGL, return
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
            func = getattr(_FBO, funcname)
        except AttributeError:
            func = None

    # Try using "alias"
    if not bool(func):
        # Some functions are known by a slightly different name
        # e.g. glDepthRangef, glClearDepthf
        if funcname.endswith('f'):
            try:
                func = getattr(_GL, funcname[:-1])
            except AttributeError:
                pass

    # Set dummy function if we could not find it
    if func is None:
        func = _make_unavailable_func(funcname)
        logger.warning('warning: %s not available' % funcname)
    return func


def _inject():
    """Copy functions from OpenGL.GL into _pyopengl namespace."""
    NS = _pyopengl2.__dict__
    for glname, ourname in _pyopengl2._functions_to_import:
        func = _get_function_from_pyopengl(glname)
        NS[ourname] = func


from . import _pyopengl2  # noqa

# Inject remaining functions from OpenGL.GL
# copies name to _pyopengl2 namespace
_inject()

# Inject all function definitions in _pyopengl2
_copy_gl_functions(_pyopengl2, globals())
