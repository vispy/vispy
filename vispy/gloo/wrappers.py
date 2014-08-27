# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np
from copy import deepcopy

from . import gl
from ..ext.six import string_types
from ..color import Color


__all__ = ('set_viewport', 'set_depth_range', 'set_front_face',
           'set_cull_face', 'set_line_width', 'set_polygon_offset',
           'clear', 'set_clear_color', 'set_clear_depth', 'set_clear_stencil',
           'set_blend_func', 'set_blend_color', 'set_blend_equation',
           'set_scissor', 'set_stencil_func', 'set_stencil_mask',
           'set_stencil_op', 'set_depth_func', 'set_depth_mask',
           'set_color_mask', 'set_sample_coverage',
           'get_state_presets', 'set_state', 'finish', 'flush',
           'get_parameter', 'read_pixels', 'set_hint',
           'get_gl_configuration', 'check_error', '_check_valid')
_setters = [s[4:] for s in __all__
            if s.startswith('set_') and s != 'set_state']


# Helpers that are needed for efficient wrapping

def _check_valid(key, val, valid):
    """Helper to check valid options"""
    if val not in valid:
        raise ValueError('%s must be one of %s, not "%s"'
                         % (key, valid, val))


def _gl_attr(x):
    """Helper to return gl.GL_x enum"""
    y = 'GL_' + x.upper()
    z = getattr(gl, y, None)
    if z is None:
        raise ValueError('gl has no attribute corresponding to name %s (%s)'
                         % (x, y))
    return z


def _gl_bool(x):
    """Helper to convert to GL boolean"""
    return gl.GL_TRUE if x else gl.GL_FALSE


def _to_args(x):
    """Convert to args representation"""
    if not isinstance(x, (list, tuple, np.ndarray)):
        x = [x]
    return x


def _check_conversion(key, valid_dict):
    """Check for existence of key in dict, return value or raise error"""
    if key not in valid_dict and key not in valid_dict.values():
        # Only show users the nice string values
        keys = [v for v in valid_dict.keys() if isinstance(key, string_types)]
        raise ValueError('value must be one of %s, not %s' % (keys, key))
    return valid_dict[key] if key in valid_dict else key


###############################################################################
# PRIMITIVE/VERTEX

#
# Viewport, DepthRangef, CullFace, FrontFace, LineWidth, PolygonOffset
#

def set_viewport(*args):
    """Set the OpenGL viewport

    This is a wrapper for gl.glViewport.

    Parameters
    ----------
    x, y, w, h : int | tuple
        X and Y coordinates, plus width and height. Can be passed in as
        individual components, or as a single tuple with four values.
    """
    x, y, w, h = args[0] if len(args) == 1 else args
    gl.glViewport(int(x), int(y), int(w), int(h))


def set_depth_range(near=0., far=1.):
    """Set depth values

    Parameters
    ----------
    near : float
        Near clipping plane.
    far : float
        Far clipping plane.
    """
    gl.glDepthRange(float(near), float(far))


def set_front_face(mode='ccw'):
    """Set which faces are front-facing

    Parameters
    ----------
    mode : str
        Can be 'cw' for clockwise or 'ccw' for counter-clockwise.
    """
    gl.glFrontFace(_gl_attr(mode))


def set_cull_face(mode='back'):
    """Set front, back, or both faces to be culled

    Parameters
    ----------
    mode : str
        Culling mode. Can be "front", "back", or "front_and_back".
    """
    gl.glCullFace(_gl_attr(mode))


def set_line_width(width=1.):
    """Set line width

    Parameters
    ----------
    width : float
        The line width.
    """
    gl.glLineWidth(float(width))


def set_polygon_offset(factor=0., units=0.):
    """Set the scale and units used to calculate depth values

    Parameters
    ----------
    factor : float
        Scale factor used to create a variable depth offset for each polygon.
    units : float
        Multiplied by an implementation-specific value to create a constant
        depth offset.
    """
    gl.glPolygonOffset(float(factor), float(units))


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
    color : bool | str | tuple | instance of Color
        Clear the color buffer bit. If not bool, ``set_clear_color`` will
        be used to set the color clear value.
    depth : bool | float
        Clear the depth buffer bit. If float, ``set_clear_depth`` will
        be used to set the depth clear value.
    stencil : bool | int
        Clear the stencil buffer bit. If int, ``set_clear_stencil`` will
        be used to set the stencil clear index.
    """
    bits = 0
    if isinstance(color, np.ndarray) or bool(color):
        if not isinstance(color, bool):
            set_clear_color(color)
        bits |= gl.GL_COLOR_BUFFER_BIT
    if depth:
        if not isinstance(depth, bool):
            set_clear_depth(depth)
        bits |= gl.GL_DEPTH_BUFFER_BIT
    if stencil:
        if not isinstance(stencil, bool):
            set_clear_stencil(stencil)
        bits |= gl.GL_STENCIL_BUFFER_BIT
    gl.glClear(bits)


def set_clear_color(color='black'):
    """Set the screen clear color

    This is a wrapper for gl.glClearColor.

    Parameters
    ----------
    color : str | tuple | instance of Color
        Color to use. See vispy.color.Color for options.
    """
    gl.glClearColor(*Color(color).rgba)


def set_clear_depth(depth=1.0):
    """Set the clear value for the depth buffer

    This is a wrapper for gl.glClearDepth.

    Parameters
    ----------
    depth : float
        The depth to use.
    """
    gl.glClearDepth(float(depth))


def set_clear_stencil(index=0):
    """Set the clear value for the stencil buffer

    This is a wrapper for gl.glClearStencil.

    Parameters
    ----------
    index : int
        The index to use when the stencil buffer is cleared.
    """
    gl.glClearStencil(int(index))


# glBlendFunc(Separate), glBlendColor, glBlendEquation(Separate)

def set_blend_func(srgb='one', drgb='zero',
                   salpha=None, dalpha=None):
    """Specify pixel arithmetic for RGB and alpha

    Parameters
    ----------
    srgb : str
        Source RGB factor.
    drgb : str
        Destination RGB factor.
    salpha : str | None
        Source alpha factor. If None, ``srgb`` is used.
    dalpha : str
        Destination alpha factor. If None, ``drgb`` is used.
    """
    salpha = srgb if salpha is None else salpha
    dalpha = drgb if dalpha is None else dalpha
    gl.glBlendFuncSeparate(_gl_attr(srgb), _gl_attr(drgb),
                           _gl_attr(salpha), _gl_attr(dalpha))


def set_blend_color(color):
    """Set the blend color

    Parameters
    ----------
    color : str | tuple | instance of Color
        Color to use. See vispy.color.Color for options.
    """
    gl.glBlendColor(*Color(color).rgba)


def set_blend_equation(mode_rgb, mode_alpha=None):
    """Specify the equation for RGB and alpha blending

    Parameters
    ----------
    mode_rgb : str
        Mode for RGB.
    mode_alpha : str | None
        Mode for Alpha. If None, ``mode_rgb`` is used.

    Notes
    -----
    See ``set_blend_equation`` for valid modes.
    """
    mode_alpha = mode_rgb if mode_alpha is None else mode_alpha
    gl.glBlendEquationSeparate(_gl_attr(mode_rgb),
                               _gl_attr(mode_alpha))


# glScissor, glStencilFunc(Separate), glStencilMask(Separate),
# glStencilOp(Separate),

def set_scissor(x, y, w, h):
    """Define the scissor box

    Parameters
    ----------
    x : int
        Left corner of the box.
    y : int
        Lower corner of the box.
    w : int
        The width of the box.
    h : int
        The height of the box.
    """
    gl.glScissor(int(x), int(y), int(w), int(h))


def set_stencil_func(func='always', ref=0, mask=8, face='front_and_back'):
    """Set front or back function and reference value

    Parameters
    ----------
    func : str
        See set_stencil_func.
    ref : int
        Reference value for the stencil test.
    mask : int
        Mask that is ANDed with ref and stored stencil value.
    face : str
        Can be 'front', 'back', or 'front_and_back'.
    """
    gl.glStencilFuncSeparate(_gl_attr(face), _gl_attr(func),
                             int(ref), int(mask))


def set_stencil_mask(mask=8, face='front_and_back'):
    """Control the front or back writing of individual bits in the stencil

    Parameters
    ----------
    mask : int
        Mask that is ANDed with ref and stored stencil value.
    face : str
        Can be 'front', 'back', or 'front_and_back'.
    """
    gl.glStencilMaskSeparate(_gl_attr(face), int(mask))


def set_stencil_op(sfail='keep', dpfail='keep', dppass='keep',
                   face='front_and_back'):
    """Set front or back stencil test actions

    Parameters
    ----------
    sfail : str
        Action to take when the stencil fails. Must be one of
        'keep', 'zero', 'replace', 'incr', 'incr_wrap',
        'decr', 'decr_wrap', or 'invert'.
    dpfail : str
        Action to take when the stencil passes.
    dppass : str
        Action to take when both the stencil and depth tests pass,
        or when the stencil test passes and either there is no depth
        buffer or depth testing is not enabled.
    face : str
        Can be 'front', 'back', or 'front_and_back'.
    """
    gl.glStencilOpSeparate(_gl_attr(face), _gl_attr(sfail),
                           _gl_attr(dpfail), _gl_attr(dppass))


# glDepthFunc, glDepthMask, glColorMask, glSampleCoverage

def set_depth_func(func='less'):
    """Specify the value used for depth buffer comparisons

    Parameters
    ----------
    func : str
        The depth comparison function. Must be one of 'never', 'less', 'equal',
        'lequal', 'greater', 'gequal', 'notequal', or 'always'.
    """
    gl.glDepthFunc(_gl_attr(func))


def set_depth_mask(flag):
    """Toggle writing into the depth buffer

    Parameters
    ----------
    flag : bool
        Whether depth writing should be enabled.
    """
    gl.glDepthMask(_gl_bool(flag))


def set_color_mask(red, green, blue, alpha):
    """Toggle writing of frame buffer color components

    Parameters
    ----------
    red : bool
        Red toggle.
    green : bool
        Green toggle.
    blue : bool
        Blue toggle.
    alpha : bool
        Alpha toggle.
    """
    gl.glColorMask(_gl_bool(red), _gl_bool(green), _gl_bool(blue),
                   _gl_bool(alpha))


def set_sample_coverage(value=1.0, invert=False):
    """Specify multisample coverage parameters

    Parameters
    ----------
    value : float
        Sample coverage value (will be clamped between 0. and 1.).
    invert : bool
        Specify if the coverage masks should be inverted.
    """
    gl.glSampleCoverage(float(value), _gl_bool(invert))


###############################################################################
# STATE

#
# glEnable/Disable
#

# NOTE: If these are updated to have things beyond glEnable/glBlendFunc
# calls, set_preset_state will need to be updated to deal with it.
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


def set_state(preset=None, **kwargs):
    """Set OpenGL rendering state, optionally using a preset

    Parameters
    ----------
    preset : str | None
        Can be one of ('opaque', 'translucent', 'additive') to use
        use reasonable defaults for these typical use cases.
    **kwargs : keyword arguments
        Other supplied keyword arguments will override any preset defaults.
        Options to be enabled or disabled should be supplied as booleans
        (e.g., ``'depth_test=True'``, ``cull_face=False``), non-boolean
        entries will be passed as arguments to ``set_*`` functions (e.g.,
        ``blend_func=('src_alpha', 'one')`` will call ``set_blend_func``).

    Notes
    -----
    This serves three purposes:

      1. Set GL state using reasonable presets.
      2. Wrapping glEnable/glDisable functionality.
      3. Convienence wrapping of other ``gloo.set_*`` functions.

    For example, one could do the following:

        >>> from vispy import gloo
        >>> gloo.set_state('translucent', depth_test=False, clear_color=(1, 1, 1, 1))  # noqa, doctest:+SKIP

    This would take the preset defaults for 'translucent', turn depth testing
    off (which would normally be on for that preset), and additionally
    set the glClearColor parameter to be white.

    Another example to showcase glEnable/glDisable wrapping:

        >>> gloo.set_state(blend=True, depth_test=True, polygon_offset_fill=False)  # noqa, doctest:+SKIP

    This would be equivalent to calling

        >>> from vispy.gloo import gl
        >>> gl.glDisable(gl.GL_BLEND)
        >>> gl.glEnable(gl.GL_DEPTH_TEST)
        >>> gl.glEnable(gl.GL_POLYGON_OFFSET_FILL)

    Or here's another example:

        >>> gloo.set_state(clear_color=(0, 0, 0, 1), blend=True, blend_func=('src_alpha', 'one'))  # noqa, doctest:+SKIP

    Thus arbitrary GL state components can be set directly using ``set_state``.
    Note that individual functions are exposed e.g., as ``set_clear_color``,
    with some more informative docstrings about those particular functions.
    """
    kwargs = deepcopy(kwargs)
    # Load preset, if supplied
    if preset is not None:
        _check_valid('preset', preset, tuple(list(_gl_presets.keys())))
        for key, val in _gl_presets[preset].items():
            # only overwrite user's input with preset if user's input is None
            if key not in kwargs:
                kwargs[key] = val

    # cull_face is an exception because GL_CULL_FACE and glCullFace both exist
    if 'cull_face' in kwargs:
        cull_face = kwargs.pop('cull_face')
        if isinstance(cull_face, bool):
            func = gl.glEnable if cull_face else gl.glDisable
            func(_gl_attr('cull_face'))
        else:
            set_cull_face(*_to_args(cull_face))

    # Now deal with other non-glEnable/glDisable args
    for s in _setters:
        if s in kwargs:
            args = _to_args(kwargs.pop(s))
            # these actually need tuples
            if s in ('blend_color', 'clear_color') and \
                    not isinstance(args[0], string_types):
                args = [args]
            globals()['set_' + s](*args)

    # check values and translate
    for key, val in kwargs.items():
        func = gl.glEnable if val else gl.glDisable
        func(_gl_attr(key))


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
    return gl.glGetParameter(_gl_attr(name))


def read_pixels(viewport=None, alpha=True):
    """Read pixels from the front buffer

    Parameters
    ----------
    viewport : array-like | None
        4-element list of x, y, w, h parameters. If None (default),
        the current GL viewport will be queried and used.
    alpha : bool
        If True (default), the returned array has 4 elements (RGBA).
        Otherwise, it has 3 (RGB).

    Returns
    -------
    pixels : array
        3D array of pixels in np.uint8 format.
    """
    if viewport is None:
        viewport = get_parameter('viewport')
    viewport = np.array(viewport, int)
    if viewport.ndim != 1 or viewport.size != 4:
        raise ValueError('viewport should be 1D 4-element array-like, not %s'
                         % (viewport,))
    x, y, w, h = viewport
    gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)  # PACK, not UNPACK
    if alpha:  # gl.GL_RGBA
        im = gl.glReadPixels(x, y, w, h, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)
    else:  # gl.gl_RGB
        im = gl.glReadPixels(x, y, w, h, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
    gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 4)
    # reshape, flip, and return
    if not isinstance(im, np.ndarray):
        im = np.frombuffer(im, np.uint8)

    if alpha:
        im.shape = h, w, 4  # RGBA
    else:
        im.shape = h, w, 3  # RGB
    im = im[::-1, :, :]  # flip the image
    return im


def set_hint(target, mode):
    """Set OpenGL drawing hint

    Parameters
    ----------
    target : str
        The target (e.g., 'fog_hint', 'line_smooth_hint', 'point_smooth_hint').
    mode : str
        The mode to set (e.g., 'fastest', 'nicest', 'dont_care').
    """
    if not all(isinstance(tm, string_types) for tm in (target, mode)):
        raise TypeError('target and mode must both be strings')
    gl.glHint(_gl_attr(target), _gl_attr(mode))


###############################################################################
# Current OpenGL configuration

def get_gl_configuration():
    """Read the current gl configuration

    This function uses constants that are not in the OpenGL ES 2.1
    namespace, so only use this on desktop systems.

    Returns
    -------
    config : dict
        The currently active OpenGL configuration.
    """
    # XXX eventually maybe we can ask `gl` whether or not we can access these
    gl.check_error('pre-config check')
    config = dict()
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
    fb_param = gl.glGetFramebufferAttachmentParameter
    # copied since they aren't in ES:
    GL_FRONT_LEFT = 1024
    GL_DEPTH = 6145
    GL_STENCIL = 6146
    GL_SRGB = 35904
    GL_FRAMEBUFFER_ATTACHMENT_COLOR_ENCODING = 33296
    GL_STEREO = 3123
    GL_DOUBLEBUFFER = 3122
    sizes = dict(red=(GL_FRONT_LEFT, 33298),
                 green=(GL_FRONT_LEFT, 33299),
                 blue=(GL_FRONT_LEFT, 33300),
                 alpha=(GL_FRONT_LEFT, 33301),
                 depth=(GL_DEPTH, 33302),
                 stencil=(GL_STENCIL, 33303))
    for key, val in sizes.items():
        config[key + '_size'] = fb_param(gl.GL_FRAMEBUFFER, val[0], val[1])
    val = fb_param(gl.GL_FRAMEBUFFER, GL_FRONT_LEFT,
                   GL_FRAMEBUFFER_ATTACHMENT_COLOR_ENCODING)
    if val not in (gl.GL_LINEAR, GL_SRGB):
        raise RuntimeError('unknown value for SRGB: %s' % val)
    config['srgb'] = True if val == GL_SRGB else False  # GL_LINEAR
    config['stereo'] = True if gl.glGetParameter(GL_STEREO) else False
    config['double_buffer'] = (True if gl.glGetParameter(GL_DOUBLEBUFFER)
                               else False)
    config['samples'] = gl.glGetParameter(gl.GL_SAMPLES)
    gl.check_error('post-config check')
    return config


def check_error():
    """Check for OpenGL errors

    For efficiency, errors are only checked periodically. This forces
    a check for OpenGL errors.
    """
    gl.check_error('gloo check')
