# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from copy import deepcopy

from ..util import logger
from . import gl


###############################################################################
# PRIMITIVE/VERTEX

#
# glViewport, XXX glDepthRangef, glCullFace, glFrontFace,
# XXX glLineWidth, glPolygonOffset
#

def set_viewport(x, y, w, h):
    """Set the OpenGL viewport

    This is a wrapper for gl.glViewport.

    Parameters
    ----------
    x : int
        X coordinate.
    y : int
        Y coordinate.
    w : int
        Viewport width.
    h : int
        Viewport height.
    """
    if not all(isinstance(v, int) for v in (x, y, w, h)):
        raise ValueError('All parameters must be integers')
    gl.glViewport(x, y, w, h)


###############################################################################
# FRAGMENT/SCREEN

#
# glClear, glClearColor, glClearDepthf, glClearStencil
#

def clear(color=True, depth=True, stencil=True):
    """Clear the screen buffers

    This is a wrapper for gl.glClear.

    Parameters
    ----------
    color : bool | tuple
        Clear the color buffer bit. If tuple, ``set_clear_color`` will
        be used to set the color clear value.
    depth : bool | float
        Clear the depth buffer bit. If float, ``set_clear_depth`` will
        be used to set the depth clear value.
    stencil : bool | int
        Clear the stencil buffer bit. If int, ``set_clear_stencil`` will
        be used to set the stencil clear index.
    """
    bits = 0
    if color:
        if not isinstance(color, bool):
            set_clear_color(color)
        bits |= gl.GL_COLOR_BUFFER_BIT
    if depth:
        if not isinstance(depth, bool):
            set_clear_depth(depth)
        bits |= gl.GL_DEPTH_BUFFER_BIT
    if stencil:
        bits |= gl.GL_STENCIL_BUFFER_BIT
    gl.glClear(bits)


def set_clear_color(color=(0., 0., 0., 1.)):
    """Set the screen clear color

    This is a wrapper for gl.glClearColor.

    Parameters
    ----------
    color : 4-element tuple
        Color to use. Defaults to black.
    """
    # XXX Eventually we can make this better with vispy.color
    if not isinstance(color, (tuple)) or len(color) != 4:
        raise ValueError('color must be a 4-element tuple')
    if not all(isinstance(c, (int, float)) for c in color):
        raise ValueError('all elements in color must be integers')
    gl.glClearColor(*color)


def set_clear_depth(depth=1.0):
    """Set the clear value for the depth buffer

    This is a wrapper for gl.glClearDepthf.

    Parameters
    ----------
    depth : float
        The depth to use.
    """
    if not isinstance(depth, float):
        raise TypeError('depth must be a float')
    gl.glClearDepthf(depth)


def set_clear_stencil(index=0):
    """Set the clear value for the stencil buffer

    This is a wrapper for gl.glClearStencil.

    Parameters
    ----------
    index : int
        The index to use when the stencil buffer is cleared.
    """
    if not isinstance(index, int):
        raise TypeError('index must be an integer')
    gl.glClearStencil(index)

#
# XXX glBlendColor, glBlendEquation, glBlendEquationSeparate, glBlendFunc,
# XXX glBlendFuncSeparate, glScissor, glStencilFunc, glStencilFuncSeparate
# XXX glStencilMask, glStencilMaskSeparate, glStencilOp, glStencilOpSeparate,
# XXX glDepthFunc, glDepthMask, glColorMask, glSampleCoverage


###############################################################################
# STATE

#
# glEnable/Disable
#

# Put user-space accessible preset names here, nest gl calls
_gl_presets = dict(
    opaque=dict(depth_test=True, cull=False, blend=False),
    translucent=dict(depth_test=True, cull=False, blend=True,
                     blend_func=('src_alpha', 'one_minus_src_alpha')),
    additive=dict(depth_test=False, cull=False, blend=True,
                  blend_func=('src_alpha', 'one'),)
)


def get_state_presets():
    """The available GL state presets

    Returns
    -------
    presets : dict
        The dictionary of presets usable with ``set_options``.
    """
    return deepcopy(_gl_presets)


_known_state_names = ('depth_test', 'blend', 'blend_func')


def get_state_names():
    """
    depth_test : bool | None
        Perform depth testing. None will not change the current state.
    blend : bool | None
        Blend. None will not change the current state.
    blend_func : tuple | None
        Blend functions to use. None will not change the current state.
        If tuple, must contain two string elements from:
        ('src_alpha', 'one_minus_src_alpha', 'one').
    cull : bool | None
        Perform face culling. None will not change the current state.
    """
    # XXX organize this somehow, integrate with _known_names and set_state
    raise NotImplementedError


def set_state(preset=None, **kwargs):
    """Set OpenGL rendering state options

    Parameters
    ----------
    preset : str | None
        If str, can be one of ('opaque', 'translucent', 'additive') to
        use reasonable defaults for these typical use cases. Other supplied
        keyword arguments following this will override any preset defaults.
    **kwargs : bool
        Boolean values to enable or disable. See ``get_state_names``
        for valid keyword arguments.
    """
    # XXX FIX THIS
    for key, val in kwargs.items():
        if key not in _known_state_names:
            raise KeyError('argument %s unknown' % key)

    # Load preset, if supplied
    _valid_presets = tuple(list(_gl_presets.keys()))
    if preset is not None:
        if preset not in _valid_presets:
            raise ValueError('preset must be one of %s, not "%s"'
                             % (_valid_presets, preset))
        for key, val in _gl_presets[preset].items():
            # only overwrite user's input with preset if user's input is None
            if key not in kwargs:
                kwargs[key] = val

    # nest these to ensure we get up-to-date "gl" namespace
    _gl_dict = dict(depth_test=gl.GL_DEPTH_TEST,
                    blend=gl.GL_BLEND,
                    cull=gl.GL_CULL_FACE)
    _gl_blend_dict = dict(src_alpha=gl.GL_SRC_ALPHA,
                          one=gl.GL_ONE,
                          one_minus_src_alpha=gl.GL_ONE_MINUS_SRC_ALPHA)

    # check vals and translate to GL
    blend_funcs = kwargs['blend_func']
    _valid_blend_funcs = tuple(list(_gl_blend_dict.keys()))
    if blend_funcs is not None:
        if not isinstance(blend_funcs, (list, tuple)) or len(blend_funcs) != 2:
            raise ValueError('blend_func must be 2-element list or tuple')
        blend_funs = list(kwargs['blend_func'])
        for bi, bf in enumerate(blend_funs):
            if bf not in _valid_blend_funcs:
                raise ValueError('blend_func "%s" must be one of %s"'
                                 % (bf, _valid_blend_funcs))
            blend_funs[bi] = _gl_blend_dict[bf]
    for key, val in kwargs.items():
        if val is not None:
            logger.debug('Setting state %s: %s' % (key, val))
            if key == 'blend_func':
                gl.glBlendFunc(*blend_funs)
            else:  # everything else
                flag = _gl_dict[key]
                if val:
                    gl.glEnable(flag)
                else:
                    gl.glDisable(flag)


#
# glFinish, glFlush, XXX glHint, glReadPixels, glGetParam
#

def finish():
    """Wait for GL commands to to finish

    This is a wrapper for glFinish().
    """
    gl.glFinish()


def flush():
    """Flush GL commands

    This is a wrapper for glFlush().
    """
    gl.glFlush()


def get_param(name):
    """Get OpenGL parameter value

    Parameters
    ----------
    name : str
        The name of the parameter to get.
    """
    # XXX need to make str->enum dict, check name, etc
    raise NotImplementedError
    gl.glGetParameter(name)
