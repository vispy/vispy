# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from ..util import logger
from . import gl


# Put user-space accessible names here, nest gl calls
_gl_presets = dict(
    opaque=dict(depth_test=True, cull=False, blend=False),
    translucent=dict(depth_test=True, cull=False, blend=True,
                     blend_func=('src_alpha', 'one_minus_src_alpha')),
    additive=dict(depth_test=False, cull=False, blend=True,
                  blend_func=('src_alpha', 'one'),)
)


def set_options(preset=None, depth_test=None, blend=None, blend_func=None,
                cull=None):
    """Set OpenGL rendering options

    Parameters
    ----------
    preset : str | None
        If str, can be one of ('opaque', 'translucent', 'additive') to
        use reasonable defaults for these typical use cases. Other supplied
        keyword arguments (below) will override the preset defaults.
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
    # store all arguments in kwargs -- we don't simply use **kwargs here
    # to take advantage of Python's built-in input checking, and for
    # making introspection and doc-building cleaner
    kwargs = dict(depth_test=depth_test, blend=blend, blend_func=blend_func,
                  cull=cull)

    # Load preset, if supplied
    _valid_presets = tuple(list(_gl_presets.keys()))
    if preset is not None:
        if preset not in _valid_presets:
            raise ValueError('preset must be one of %s, not "%s"'
                             % (_valid_presets, preset))
        for key, val in _gl_presets[preset].items():
            # only overwrite user's input with preset if user's input is None
            if kwargs[key] is None:
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
            logger.info('Setting %s: %s' % (key, val))
            if key == 'blend_func':
                gl.glBlendFunc(*blend_funs)
            else:  # everything else
                flag = _gl_dict[key]
                if val:
                    gl.glEnable(flag)
                else:
                    gl.glDisable(flag)


def set_clear_color(color=(0, 0, 0, 1)):
    """Set the screen clear color

    This is a simple wrapper for gl.glClearColor.

    Parameters
    ----------
    color : 4-element tuple
        Color to use. Defaults to black.
    """
    # XXX Eventually we can make this better with vispy.color
    if not isinstance(color, (tuple)) or len(color) != 4:
        raise ValueError('color must be a 4-element tuple')
    if not all(isinstance(c, int) for c in color):
        raise ValueError('all elements in color must be integers')
    gl.glClearColor(*color)


def clear(color_buffer=True, depth_buffer=True):
    """Clear the screen buffers

    This is a simple wrapper for gl.glClear.

    Parameters
    ----------
    color_buffer : bool
        Clear the color buffer bit.
    depth_buffer : bool
        Clear the depth buffer bit.
    """
    bits = 0
    if color_buffer:
        bits |= gl.GL_COLOR_BUFFER_BIT
    if depth_buffer:
        bits |= gl.GL_DEPTH_BUFFER_BIT
    gl.glClear(bits)


def set_viewport(x, y, w, h):
    """Set the OpenGL viewport

    This is a simple wrapper for gl.glViewport.

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
