# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from copy import deepcopy
import numpy as np

from ..util import logger
from ..util.six import string_types
from . import gl


def _check_valid(key, val, valid):
    if val not in valid:
        raise ValueError('%s must be one of %s, not "%s"'
                         % (key, valid, val))


###############################################################################
# PRIMITIVE/VERTEX

#
# Viewport, DepthRangef, CullFace, FrontFace, LineWidth, PolygonOffset
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


def set_depth_range(near, far):
    """Set depth values

    Parameters
    ----------
    near : float
        Near clipping plane.
    far : float
        Far clipping plane.
    """
    near = float(near)
    far = float(far)
    gl.glDepthRangef(near, far)


def set_front_face(mode):
    """Set which faces are front-facing

    Parameters
    ----------
    mode : str
        Can be 'cw' for clockwise or 'ccw' for counter-clockwise.
    """
    _check_valid('mode', mode, ('cw', 'ccw'))
    gl.glFrontFace(getattr(gl, 'GL_' + mode.upper()))


def set_cull_face(mode):
    """Set front, back, or both faces to be culled

    Parameters
    ----------
    mode : str
        Culling mode. Can be "front", "back", or "front_and_back".
    """
    _check_valid('mode', mode, ('front', 'back', 'front_and_back'))
    gl.glCullFace(getattr(gl, 'GL_' + mode.upper()))


def set_line_width(width):
    """Set line width

    Parameters
    ----------
    width : float
        The line width.
    """
    width = float(width)
    gl.glLineWidth(width)


def set_polygon_offset(factor, units):
    """Set the scale and units used to calculate depth values

    Parameters
    ----------
    factor : float
        Scale factor used to create a variable depth offset for each polygon.
    units : float
        Multiplied by an implementation-specific value to create a constant
        depth offset.
    """
    factor = float(factor)
    units = float(units)
    gl.glPolygonOffset(factor, units)


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
# glBlendFunc, XXX glBlendColor, glBlendEquation, glBlendEquationSeparate,
# XXX glBlendFuncSeparate, glScissor, glStencilFunc, glStencilFuncSeparate
# XXX glStencilMask, glStencilMaskSeparate, glStencilOp, glStencilOpSeparate,
# XXX glDepthFunc, glDepthMask, glColorMask, glSampleCoverage
#

_gl_blend_list = ['src_color', 'one_minus_src_color', 'zero', 'one',
                  'dst_color', 'one_minus_dst_color',
                  'src_alpha', 'one_minus_src_alpha',
                  'dst_alpha', 'one_minus_dst_alpha',
                  'constant_color', 'one_minus_constant_color',
                  'constant_alpha', 'one_minus_constant_alpha']


def set_blend_func(sfactor, dfactor):
    """Set blend function

    Parameters
    ----------
    sfactor : str
        Source factor.
    dfactor : str
        Destination factor.
    """
    # check vals and translate to GL
    for fact, name in zip((sfactor, dfactor), ('sfactor', 'dfactor')):
        _check_valid(name, fact, _gl_blend_list)
    gl_sfactor = getattr(gl, 'GL_' + sfactor.upper())
    gl_dfactor = getattr(gl, 'GL_' + dfactor.upper())
    res = gl.glBlendFunc(gl_sfactor, gl_dfactor)
    if res in (gl.GL_INVALID_ENUM, gl.GL_INVALID_VALUE):
        raise RuntimeError('could not set blend functions')


###############################################################################
# STATE

#
# glEnable/Disable
#

# Put user-space accessible preset names here, nest gl calls
_gl_presets = dict(
    opaque=dict(depth_test=True, cull_face=False, blend=False),
    translucent=dict(depth_test=True, cull_face=False, blend=True,
                     blend_func=('src_alpha', 'one_minus_src_alpha')),
    additive=dict(depth_test=False, cull_face=False, blend=True,
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


def set_preset_state(preset, **kwargs):
    """Set OpenGL rendering state using a preset

    Parameters
    ----------
    preset : str
        Can be one of ('opaque', 'translucent', 'additive') to use
        use reasonable defaults for these typical use cases.
    **kwargs : bool
        Other supplied keyword arguments will override any preset defaults.
        These will be passed to ``set_state``.
    """
    kwargs = deepcopy(kwargs)
    # Load preset, if supplied
    _check_valid('preset', preset, tuple(list(_gl_presets.keys())))
    for key, val in _gl_presets[preset].items():
        # only overwrite user's input with preset if user's input is None
        if key not in kwargs:
            kwargs[key] = val
    # XXX should expand below if things are added to presets
    # Deal with pesky non-glEnable/glDisable args
    if 'blend_func' in kwargs:
        set_blend_func(*kwargs.pop('blend_func'))
    # Pass to set_state
    set_state(**kwargs)


def set_state(**kwargs):
    """Set OpenGL rendering state options

    Parameters
    ----------
    **kwargs : bool
        Boolean values to enable or disable.
    """
    # check values and translate
    kwargs = deepcopy(kwargs)
    for key, val in kwargs.items():
        if not isinstance(val, bool):
            raise TypeError('All inputs to set_state must be boolean')
        gl_key = getattr(gl, 'GL_' + key.upper(), None)
        if gl_key is None:
            raise KeyError('argument %s unknown' % key)
        func = gl.glEnable if val else gl.glDisable
        func(gl_key)


#
# glFinish, glFlush, glGetParameter, glReadPixels, glHint
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


def get_parameter(name):
    """Get OpenGL parameter value

    Parameters
    ----------
    name : str
        The name of the parameter to get.
    """
    if not isinstance(name, string_types):
        raise TypeError('name bust be a string')
    gl_parameter = getattr(gl, 'GL_' + name.upper(), None)
    if gl_parameter is None:
        raise ValueError('gl has no attribute corresponding to name %s' % name)
    return gl.glGetParameter(gl_parameter)


def read_pixels(viewport=None):
    """Read pixels from the front buffer

    Parameters
    ----------
    viewport : array-like | None
        4-element list of x, y, w, h parameters. If None (default),
        the current GL viewport will be queried and used.

    Returns
    -------
    pixels : array
        2D array of pixels in np.uint8 format.
    """
    if viewport is None:
        viewport = get_parameter('viewport')
    else:
        viewport = np.array(viewport, int)
        if viewport.ndim != 1 or viewport.size != 4:
            raise ValueError('viewport must be 1D 4-element array-like')
    x, y, w, h = viewport
    gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)  # PACK, not UNPACK
    im = gl.glReadPixels(x, y, w, h, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
    gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 4)
    # reshape, flip, and return
    if not isinstance(im, np.ndarray):
        im = np.frombuffer(im, np.uint8)
    im.shape = h, w, 3
    return im


def hint(target, mode):
    """Set OpenGL drawing hint

    Parameters
    ----------
    target : str
        The target (e.g., 'fog', 'line_smooth', 'point_smooth').
    mode : str
        The mode to set (e.g., 'fastest', 'nicest', 'dont_care').
    """
    if not all(isinstance(tm, string_types) for tm in (target, mode)):
        raise TypeError('target and mode must both be strings')
    gl_target = getattr(gl, 'GL_' + target.upper() + '_HINT', None)
    gl_mode = getattr(gl, 'GL_' + mode.upper(), None)
    for tm, gl_tm, name in zip((target, mode), (gl_target, gl_mode),
                               ('target', 'mode')):
        if gl_tm is None:
            raise ValueError('gl has no hint %s %s' % (name, tm))
    val = gl.glHint()
    if val in (gl.GL_INVALID_ENUM, gl.GL_INVALID_OPERATION):
        raise RuntimeError('hint could not be set')
