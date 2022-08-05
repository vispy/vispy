# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np
from copy import deepcopy

from . import gl
from ..color import Color
from ..util import logger


__all__ = ('set_viewport', 'set_depth_range', 'set_front_face',  # noqa
           'set_cull_face', 'set_line_width', 'set_polygon_offset',  # noqa
           'clear', 'set_clear_color', 'set_clear_depth', 'set_clear_stencil',  # noqa
           'set_blend_func', 'set_blend_color', 'set_blend_equation',  # noqa
           'set_scissor', 'set_stencil_func', 'set_stencil_mask',  # noqa
           'set_stencil_op', 'set_depth_func', 'set_depth_mask',  # noqa
           'set_color_mask', 'set_sample_coverage',  # noqa
           'get_state_presets', 'set_state', 'finish', 'flush',  # noqa
           'read_pixels', 'set_hint',  # noqa
           'get_gl_configuration', '_check_valid',
           'GL_PRESETS',
           'GlooFunctions', 'global_gloo_functions', )

_setters = [s[4:] for s in __all__
            if s.startswith('set_') and s != 'set_state']

# NOTE: If these are updated to have things beyond glEnable/glBlendFunc
# calls, set_state will need to be updated to deal with it.
#: Some OpenGL state presets for common use cases: 'opaque', 'translucent',
#: 'additive'.
#:
#: To be used in :func:`.set_state`.
GL_PRESETS = {
    'opaque': dict(
        depth_test=True,
        cull_face=False,
        blend=False),
    'translucent': dict(
        depth_test=True,
        cull_face=False,
        blend=True,
        blend_func=('src_alpha', 'one_minus_src_alpha', 'zero', 'one'),
        blend_equation='func_add'),
    'additive': dict(
        depth_test=False,
        cull_face=False,
        blend=True,
        blend_func=('src_alpha', 'one'),
        blend_equation='func_add'),
}


def get_current_canvas():
    """Proxy for context.get_current_canvas to avoud circular import.
    This function replaces itself with the real function the first
    time it is called. (Bah)
    """
    from .context import get_current_canvas
    globals()['get_current_canvas'] = get_current_canvas
    return get_current_canvas()


# Helpers that are needed for efficient wrapping

def _check_valid(key, val, valid):
    """Helper to check valid options"""
    if val not in valid:
        raise ValueError('%s must be one of %s, not "%s"'
                         % (key, valid, val))


def _to_args(x):
    """Convert to args representation"""
    if not isinstance(x, (list, tuple, np.ndarray)):
        x = [x]
    return x


def _check_conversion(key, valid_dict):
    """Check for existence of key in dict, return value or raise error"""
    if key not in valid_dict and key not in valid_dict.values():
        # Only show users the nice string values
        keys = [v for v in valid_dict.keys() if isinstance(v, str)]
        raise ValueError('value must be one of %s, not %s' % (keys, key))
    return valid_dict[key] if key in valid_dict else key


class BaseGlooFunctions(object):
    """Class that provides a series of GL functions that do not fit
    in the object oriented part of gloo. An instance of this class is
    associated with each canvas.
    """

    ##########################################################################
    # PRIMITIVE/VERTEX

    #
    # Viewport, DepthRangef, CullFace, FrontFace, LineWidth, PolygonOffset
    #

    def set_viewport(self, *args):
        """Set the OpenGL viewport

        This is a wrapper for gl.glViewport.

        Parameters
        ----------
        *args : tuple
            X and Y coordinates, plus width and height. Can be passed in as
            individual components, or as a single tuple with four values.
        """
        x, y, w, h = args[0] if len(args) == 1 else args
        self.glir.command('FUNC', 'glViewport', int(x), int(y), int(w), int(h))

    def set_depth_range(self, near=0., far=1.):
        """Set depth values

        Parameters
        ----------
        near : float
            Near clipping plane.
        far : float
            Far clipping plane.
        """
        self.glir.command('FUNC', 'glDepthRange', float(near), float(far))

    def set_front_face(self, mode='ccw'):
        """Set which faces are front-facing

        Parameters
        ----------
        mode : str
            Can be 'cw' for clockwise or 'ccw' for counter-clockwise.
        """
        self.glir.command('FUNC', 'glFrontFace', mode)

    def set_cull_face(self, mode='back'):
        """Set front, back, or both faces to be culled

        Parameters
        ----------
        mode : str
            Culling mode. Can be "front", "back", or "front_and_back".
        """
        self.glir.command('FUNC', 'glCullFace', mode)

    def set_line_width(self, width=1.):
        """Set line width

        Parameters
        ----------
        width : float
            The line width.
        """
        width = float(width)
        if width < 0:
            raise RuntimeError('Cannot have width < 0')
        self.glir.command('FUNC', 'glLineWidth', width)

    def set_polygon_offset(self, factor=0., units=0.):
        """Set the scale and units used to calculate depth values

        Parameters
        ----------
        factor : float
            Scale factor used to create a variable depth offset for
            each polygon.
        units : float
            Multiplied by an implementation-specific value to create a
            constant depth offset.
        """
        self.glir.command('FUNC', 'glPolygonOffset', float(factor),
                          float(units))

    ##########################################################################
    # FRAGMENT/SCREEN

    #
    # glClear, glClearColor, glClearDepthf, glClearStencil
    #

    def clear(self, color=True, depth=True, stencil=True):
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
                self.set_clear_color(color)
            bits |= gl.GL_COLOR_BUFFER_BIT
        if depth:
            if not isinstance(depth, bool):
                self.set_clear_depth(depth)
            bits |= gl.GL_DEPTH_BUFFER_BIT
        if stencil:
            if not isinstance(stencil, bool):
                self.set_clear_stencil(stencil)
            bits |= gl.GL_STENCIL_BUFFER_BIT
        self.glir.command('FUNC', 'glClear', bits)

    def set_clear_color(self, color='black', alpha=None):
        """Set the screen clear color

        This is a wrapper for gl.glClearColor.

        Parameters
        ----------
        color : str | tuple | instance of Color
            Color to use. See vispy.color.Color for options.
        alpha : float | None
            Alpha to use.
        """
        self.glir.command('FUNC', 'glClearColor', *Color(color, alpha).rgba)

    def set_clear_depth(self, depth=1.0):
        """Set the clear value for the depth buffer

        This is a wrapper for gl.glClearDepth.

        Parameters
        ----------
        depth : float
            The depth to use.
        """
        self.glir.command('FUNC', 'glClearDepth', float(depth))

    def set_clear_stencil(self, index=0):
        """Set the clear value for the stencil buffer

        This is a wrapper for gl.glClearStencil.

        Parameters
        ----------
        index : int
            The index to use when the stencil buffer is cleared.
        """
        self.glir.command('FUNC', 'glClearStencil', int(index))

    # glBlendFunc(Separate), glBlendColor, glBlendEquation(Separate)

    def set_blend_func(self, srgb='one', drgb='zero',
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
        self.glir.command('FUNC', 'glBlendFuncSeparate',
                          srgb, drgb, salpha, dalpha)

    def set_blend_color(self, color):
        """Set the blend color

        Parameters
        ----------
        color : str | tuple | instance of Color
            Color to use. See vispy.color.Color for options.
        """
        self.glir.command('FUNC', 'glBlendColor', *Color(color).rgba)

    def set_blend_equation(self, mode_rgb, mode_alpha=None):
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
        self.glir.command('FUNC', 'glBlendEquationSeparate',
                          mode_rgb, mode_alpha)

    # glScissor, glStencilFunc(Separate), glStencilMask(Separate),
    # glStencilOp(Separate),

    def set_scissor(self, x, y, w, h):
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
        self.glir.command('FUNC', 'glScissor', int(x), int(y), int(w), int(h))

    def set_stencil_func(self, func='always', ref=0, mask=8,
                         face='front_and_back'):
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
        self.glir.command('FUNC', 'glStencilFuncSeparate',
                          face, func, int(ref), int(mask))

    def set_stencil_mask(self, mask=8, face='front_and_back'):
        """Control the front or back writing of individual bits in the stencil

        Parameters
        ----------
        mask : int
            Mask that is ANDed with ref and stored stencil value.
        face : str
            Can be 'front', 'back', or 'front_and_back'.
        """
        self.glir.command('FUNC', 'glStencilMaskSeparate', face, int(mask))

    def set_stencil_op(self, sfail='keep', dpfail='keep', dppass='keep',
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
        self.glir.command('FUNC', 'glStencilOpSeparate',
                          face, sfail, dpfail, dppass)

    # glDepthFunc, glDepthMask, glColorMask, glSampleCoverage

    def set_depth_func(self, func='less'):
        """Specify the value used for depth buffer comparisons

        Parameters
        ----------
        func : str
            The depth comparison function. Must be one of 'never', 'less',
            'equal', 'lequal', 'greater', 'gequal', 'notequal', or 'always'.
        """
        self.glir.command('FUNC', 'glDepthFunc', func)

    def set_depth_mask(self, flag):
        """Toggle writing into the depth buffer

        Parameters
        ----------
        flag : bool
            Whether depth writing should be enabled.
        """
        self.glir.command('FUNC', 'glDepthMask', bool(flag))

    def set_color_mask(self, red, green, blue, alpha):
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
        self.glir.command('FUNC', 'glColorMask', bool(red), bool(green),
                          bool(blue), bool(alpha))

    def set_sample_coverage(self, value=1.0, invert=False):
        """Specify multisample coverage parameters

        Parameters
        ----------
        value : float
            Sample coverage value (will be clamped between 0. and 1.).
        invert : bool
            Specify if the coverage masks should be inverted.
        """
        self.glir.command('FUNC', 'glSampleCoverage', float(value),
                          bool(invert))

    ##########################################################################
    # STATE

    #
    # glEnable/Disable
    #

    def get_state_presets(self):
        """The available GL state :data:`presets <.GL_PRESETS>`.

        Returns
        -------
        presets : dict
            The dictionary of presets usable with :func:`.set_state`.
        """
        return deepcopy(GL_PRESETS)

    def set_state(self, preset=None, **kwargs):
        """Set the OpenGL rendering state, optionally using a preset.

        Parameters
        ----------
        preset : {'opaque', 'translucent', 'additive'}, optional
            A named state :data:`preset <.GL_PRESETS>` for typical use cases.

        **kwargs : keyword arguments
            Other supplied keyword arguments will override any preset defaults.
            Options to be enabled or disabled should be supplied as booleans
            (e.g., ``'depth_test=True'``, ``cull_face=False``), non-boolean
            entries will be passed as arguments to ``set_*`` functions (e.g.,
            ``blend_func=('src_alpha', 'one')`` will call :func:`.set_blend_func`).

        Notes
        -----
        This serves three purposes:

        1. Set GL state using reasonable presets.
        2. Wrapping glEnable/glDisable functionality.
        3. Convienence wrapping of other ``gloo.set_*`` functions.

        For example, one could do the following:

            >>> from vispy import gloo
            >>> gloo.set_state('translucent', depth_test=False, clear_color=(1, 1, 1, 1))  # noqa, doctest:+SKIP

        This would take the preset defaults for 'translucent', turn
        depth testing off (which would normally be on for that preset),
        and additionally set the glClearColor parameter to be white.

        Another example to showcase glEnable/glDisable wrapping:

            >>> gloo.set_state(blend=True, depth_test=True, polygon_offset_fill=False)  # noqa, doctest:+SKIP

        This would be equivalent to calling

            >>> from vispy.gloo import gl
            >>> gl.glDisable(gl.GL_BLEND)
            >>> gl.glEnable(gl.GL_DEPTH_TEST)
            >>> gl.glEnable(gl.GL_POLYGON_OFFSET_FILL)

        Or here's another example:

            >>> gloo.set_state(clear_color=(0, 0, 0, 1), blend=True, blend_func=('src_alpha', 'one'))  # noqa, doctest:+SKIP

        Thus arbitrary GL state components can be set directly using
        ``set_state``. Note that individual functions are exposed e.g.,
        as ``set_clear_color``, with some more informative docstrings
        about those particular functions.
        """
        kwargs = deepcopy(kwargs)

        # Load preset, if supplied
        if preset is not None:
            _check_valid('preset', preset, tuple(list(GL_PRESETS.keys())))
            for key, val in GL_PRESETS[preset].items():
                # only overwrite user input with preset if user's input is None
                if key not in kwargs:
                    kwargs[key] = val

        # cull_face is an exception because GL_CULL_FACE, glCullFace both exist
        if 'cull_face' in kwargs:
            cull_face = kwargs.pop('cull_face')
            if isinstance(cull_face, bool):
                funcname = 'glEnable' if cull_face else 'glDisable'
                self.glir.command('FUNC', funcname, 'cull_face')
            else:
                self.glir.command('FUNC', 'glEnable', 'cull_face')
                self.set_cull_face(*_to_args(cull_face))

        # Line width needs some special care ...
        if 'line_width' in kwargs:
            line_width = kwargs.pop('line_width')
            self.glir.command('FUNC', 'glLineWidth', line_width)
        if 'line_smooth' in kwargs:
            line_smooth = kwargs.pop('line_smooth')
            funcname = 'glEnable' if line_smooth else 'glDisable'
            line_smooth_enum_value = 2848  # int(GL.GL_LINE_SMOOTH)
            self.glir.command('FUNC', funcname, line_smooth_enum_value)

        # Iterate over kwargs
        for key, val in kwargs.items():
            if key in _setters:
                # Setter
                args = _to_args(val)
                # these actually need tuples
                if key in ('blend_color', 'clear_color') and \
                        not isinstance(args[0], str):
                    args = [args]
                getattr(self, 'set_' + key)(*args)
            else:
                # Enable / disable
                funcname = 'glEnable' if val else 'glDisable'
                self.glir.command('FUNC', funcname, key)

    #
    # glFinish, glFlush, glReadPixels, glHint
    #

    def finish(self):
        """Wait for GL commands to to finish

        This creates a GLIR command for glFinish and then processes the
        GLIR commands. If the GLIR interpreter is remote (e.g. WebGL), this
        function will return before GL has finished processing the commands.
        """
        if hasattr(self, 'flush_commands'):
            context = self
        else:
            context = get_current_canvas().context
        context.glir.command('FUNC', 'glFinish')
        context.flush_commands()  # Process GLIR commands

    def flush(self):
        """Flush GL commands

        This is a wrapper for glFlush(). This also flushes the GLIR
        command queue.
        """
        if hasattr(self, 'flush_commands'):
            context = self
        else:
            context = get_current_canvas().context
        context.glir.command('FUNC', 'glFlush')
        context.flush_commands()  # Process GLIR commands

    def set_hint(self, target, mode):
        """Set OpenGL drawing hint

        Parameters
        ----------
        target : str
            The target, e.g. 'fog_hint', 'line_smooth_hint',
            'point_smooth_hint'.
        mode : str
            The mode to set (e.g., 'fastest', 'nicest', 'dont_care').
        """
        if not all(isinstance(tm, str) for tm in (target, mode)):
            raise TypeError('target and mode must both be strings')
        self.glir.command('FUNC', 'glHint', target, mode)


class GlooFunctions(BaseGlooFunctions):

    @property
    def glir(self):
        """The GLIR queue corresponding to the current canvas"""
        canvas = get_current_canvas()
        if canvas is None:
            msg = ("If you want to use gloo without vispy.app, " +
                   "use a gloo.context.FakeCanvas.")
            raise RuntimeError('Gloo requires a Canvas to run.\n' + msg)
        return canvas.context.glir


# Create global functions object and inject names here

# GlooFunctions without queue: use queue of canvas that is current at call-time
global_gloo_functions = GlooFunctions()

for name in dir(global_gloo_functions):
    if name.startswith('_') or name in ('glir'):
        continue
    fun = getattr(global_gloo_functions, name)
    if callable(fun):
        globals()[name] = fun


# Functions that do not use the glir queue


def read_pixels(viewport=None, alpha=True, mode='color', out_type='unsigned_byte'):
    """Read pixels from the currently selected buffer.

    Under most circumstances, this function reads from the front buffer.
    Unlike all other functions in vispy.gloo, this function directly executes
    an OpenGL command.

    Parameters
    ----------
    viewport : array-like | None
        4-element list of x, y, w, h parameters. If None (default),
        the current GL viewport will be queried and used.
    alpha : bool
        If True (default), the returned array has 4 elements (RGBA).
        If False, it has 3 (RGB). This only effects the color mode.
    mode : str
        Type of buffer data to read. Can be one of 'colors', 'depth',
        or 'stencil'. See returns for more information.
    out_type : str | dtype
        Can be 'unsigned_byte' or 'float'. Note that this does not
        use casting, but instead determines how values are read from
        the current buffer. Can also be numpy dtypes ``np.uint8``,
        ``np.ubyte``, or ``np.float32``.

    Returns
    -------
    pixels : array
        3D array of pixels in np.uint8 or np.float32 format.
        The array shape is (h, w, 3) or (h, w, 4) for colors mode,
        with the top-left corner of the framebuffer at index [0, 0] in the
        returned array. If 'mode' is depth or stencil then the last dimension
        is 1.
    """
    _check_valid('mode', mode, ['color', 'depth', 'stencil'])

    # Check whether the GL context is direct or remote
    context = get_current_canvas().context
    if context.shared.parser.is_remote():
        raise RuntimeError('Cannot use read_pixels() with remote GLIR parser')

    finish()  # noqa - finish first, also flushes GLIR commands
    type_dict = {'unsigned_byte': gl.GL_UNSIGNED_BYTE,
                 np.uint8: gl.GL_UNSIGNED_BYTE,
                 'float': gl.GL_FLOAT,
                 np.float32: gl.GL_FLOAT}
    type_ = _check_conversion(out_type, type_dict)
    if viewport is None:
        viewport = gl.glGetParameter(gl.GL_VIEWPORT)
    viewport = np.array(viewport, int)
    if viewport.ndim != 1 or viewport.size != 4:
        raise ValueError('viewport should be 1D 4-element array-like, not %s'
                         % (viewport,))
    x, y, w, h = viewport
    gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)  # PACK, not UNPACK
    if mode == 'depth':
        fmt = gl.GL_DEPTH_COMPONENT
        shape = (h, w, 1)
    elif mode == 'stencil':
        fmt = gl.GL_STENCIL_INDEX8
        shape = (h, w, 1)
    elif alpha:
        fmt = gl.GL_RGBA
        shape = (h, w, 4)
    else:
        fmt = gl.GL_RGB
        shape = (h, w, 3)
    im = gl.glReadPixels(x, y, w, h, fmt, type_)
    gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 4)
    # reshape, flip, and return
    if not isinstance(im, np.ndarray):
        np_dtype = np.uint8 if type_ == gl.GL_UNSIGNED_BYTE else np.float32
        im = np.frombuffer(im, np_dtype)

    im.shape = shape
    im = im[::-1, ...]  # flip the image
    return im


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
    canvas = get_current_canvas()
    fbo = 0 if canvas is None else canvas._backend._vispy_get_fb_bind_location()
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo)
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
        try:
            param = fb_param(gl.GL_FRAMEBUFFER, val[0], val[1])
            gl.check_error('post-config check')
        except RuntimeError as exp:
            logger.warning('Failed to get size %s: %s' % (key, exp))
        else:
            config[key + '_size'] = param

    try:
        val = fb_param(gl.GL_FRAMEBUFFER, GL_FRONT_LEFT,
                       GL_FRAMEBUFFER_ATTACHMENT_COLOR_ENCODING)
        gl.check_error('post-config check')
    except RuntimeError as exp:
        logger.warning('Failed to get sRGB: %s' % (exp,))
    else:
        if val not in (gl.GL_LINEAR, GL_SRGB):
            logger.warning('unknown value for SRGB: %s' % val)
        else:
            config['srgb'] = (val == GL_SRGB)

    for key, enum in (('stereo', GL_STEREO),
                      ('double_buffer', GL_DOUBLEBUFFER)):
        val = gl.glGetParameter(enum)
        try:
            gl.check_error('post-config check')
        except RuntimeError as exp:
            logger.warning('Failed to get %s: %s' % (key, exp))
        else:
            config[key] = bool(val)
    config['samples'] = gl.glGetParameter(gl.GL_SAMPLES)
    gl.check_error('post-config check')
    return config
