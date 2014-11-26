# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division  # just to be safe...

import numpy as np
from copy import deepcopy

from ..ext.six import string_types, iterkeys
from ..util import logger
from ._color_dict import _color_dict


###############################################################################
# User-friendliness helpers

def _string_to_rgb(color):
    """Convert user string or hex color to color array (length 3 or 4)"""
    if not color.startswith('#'):
        if color.lower() not in _color_dict:
            raise ValueError('Color "%s" unknown' % color)
        color = _color_dict[color]
        assert color[0] == '#'
    # hex color
    color = color[1:]
    lc = len(color)
    if lc in (3, 4):
        color = ''.join(c + c for c in color)
        lc = len(color)
    if lc not in (6, 8):
        raise ValueError('Hex color must have exactly six or eight '
                         'elements following the # sign')
    color = np.array([int(color[i:i+2], 16) / 255. for i in range(0, lc, 2)])
    return color


def _user_to_rgba(color, expand=True, clip=False):
    """Convert color(s) from any set of fmts (str/hex/arr) to RGB(A) array"""
    if color is None:
        color = np.zeros(4, np.float32)
    if isinstance(color, string_types):
        color = _string_to_rgb(color)
    elif isinstance(color, ColorArray):
        color = color.rgba
    # We have to treat this specially
    elif isinstance(color, (list, tuple)):
        if any(isinstance(c, string_types) for c in color):
            color = [_user_to_rgba(c, expand=expand, clip=clip) for c in color]
            if any(len(c) > 1 for c in color):
                raise RuntimeError('could not parse colors, are they nested?')
            color = [c[0] for c in color]
    color = np.atleast_2d(color).astype(np.float32)
    if color.shape[1] not in (3, 4):
        raise ValueError('color must have three or four elements')
    if expand and color.shape[1] == 3:  # only expand if requested
        color = np.concatenate((color, np.ones((color.shape[0], 1))),
                               axis=1)
    if color.min() < 0 or color.max() > 1:
        if clip:
            color = np.clip(color, 0, 1)
        else:
            raise ValueError("Color values must be between 0 and 1 (or use "
                             "clip=True to automatically clip the values).")
    return color


def _check_color_dim(val):
    """Ensure val is Nx(n_col), usually Nx3"""
    val = np.atleast_2d(val)
    if val.shape[1] not in (3, 4):
        raise RuntimeError('Value must have second dimension of size 3 or 4')
    return val, val.shape[1]


def _array_clip_val(val):
    """Helper to turn val into array and clip between 0 and 1"""
    val = np.array(val)
    if val.max() > 1 or val.min() < 0:
        logger.warning('value will be clipped between 0 and 1')
    val[...] = np.clip(val, 0, 1)
    return val


###############################################################################
# RGB<->HEX conversion

def _hex_to_rgba(hexs):
    """Convert hex to rgba, permitting alpha values in hex"""
    hexs = np.atleast_1d(np.array(hexs, '|U9'))
    out = np.ones((len(hexs), 4), np.float32)
    for hi, h in enumerate(hexs):
        assert isinstance(h, string_types)
        off = 1 if h[0] == '#' else 0
        assert len(h) in (6+off, 8+off)
        e = (len(h)-off) // 2
        out[hi, :e] = [int(h[i:i+2], 16) / 255.
                       for i in range(off, len(h), 2)]
    return out


def _rgb_to_hex(rgbs):
    """Convert rgb to hex triplet"""
    rgbs, n_dim = _check_color_dim(rgbs)
    return np.array(['#%02x%02x%02x' % tuple((255*rgb[:3]).astype(np.uint8))
                     for rgb in rgbs], '|U7')


###############################################################################
# RGB<->HSV conversion

def _rgb_to_hsv(rgbs):
    """Convert Nx3 or Nx4 rgb to hsv"""
    rgbs, n_dim = _check_color_dim(rgbs)
    hsvs = list()
    for rgb in rgbs:
        rgb = rgb[:3]  # don't use alpha here
        idx = np.argmax(rgb)
        val = rgb[idx]
        c = val - np.min(rgb)
        if c == 0:
            hue = 0
            sat = 0
        else:
            if idx == 0:  # R == max
                hue = ((rgb[1] - rgb[2]) / c) % 6
            elif idx == 1:  # G == max
                hue = (rgb[2] - rgb[0]) / c + 2
            else:  # B == max
                hue = (rgb[0] - rgb[1]) / c + 4
            hue *= 60
            sat = c / val
        hsv = [hue, sat, val]
        hsvs.append(hsv)
    hsvs = np.array(hsvs, dtype=np.float32)
    if n_dim == 4:
        hsvs = np.concatenate((hsvs, rgbs[:, 3]), axis=1)
    return hsvs


def _hsv_to_rgb(hsvs):
    """Convert Nx3 or Nx4 hsv to rgb"""
    hsvs, n_dim = _check_color_dim(hsvs)
    # In principle, we *might* be able to vectorize this, but might as well
    # wait until a compelling use case appears
    rgbs = list()
    for hsv in hsvs:
        c = hsv[1] * hsv[2]
        m = hsv[2] - c
        hp = hsv[0] / 60
        x = c * (1 - abs(hp % 2 - 1))
        if 0 <= hp < 1:
            r, g, b = c, x, 0
        elif hp < 2:
            r, g, b = x, c, 0
        elif hp < 3:
            r, g, b = 0, c, x
        elif hp < 4:
            r, g, b = 0, x, c
        elif hp < 5:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        rgb = [r + m, g + m, b + m]
        rgbs.append(rgb)
    rgbs = np.array(rgbs, dtype=np.float32)
    if n_dim == 4:
        rgbs = np.concatenate((rgbs, hsvs[:, 3]), axis=1)
    return rgbs


###############################################################################
# RGB<->CIELab conversion

# These numbers are adapted from MIT-licensed MATLAB code for
# Lab<->RGB conversion. They provide an XYZ<->RGB conversion matrices,
# w/D65 white point normalization built in.

#_rgb2xyz = np.array([[0.412453, 0.357580, 0.180423],
#                     [0.212671, 0.715160, 0.072169],
#                     [0.019334, 0.119193, 0.950227]])
#_white_norm = np.array([0.950456, 1.0, 1.088754])
#_rgb2xyz /= _white_norm[:, np.newaxis]
#_rgb2xyz_norm = _rgb2xyz.T
_rgb2xyz_norm = np.array([[0.43395276, 0.212671, 0.01775791],
                         [0.37621941, 0.71516, 0.10947652],
                         [0.18982783, 0.072169, 0.87276557]])

#_xyz2rgb = np.array([[3.240479, -1.537150, -0.498535],
#                     [-0.969256, 1.875992, 0.041556],
#                     [0.055648, -0.204043, 1.057311]])
#_white_norm = np.array([0.950456, 1., 1.088754])
#_xyz2rgb *= _white_norm[np.newaxis, :]
_xyz2rgb_norm = np.array([[3.07993271, -1.53715, -0.54278198],
                          [-0.92123518, 1.875992, 0.04524426],
                          [0.05289098, -0.204043, 1.15115158]])


def _rgb_to_lab(rgbs):
    rgbs, n_dim = _check_color_dim(rgbs)
    # convert RGB->XYZ
    xyz = rgbs[:, :3].copy()  # a misnomer for now but will end up being XYZ
    over = xyz > 0.04045
    xyz[over] = ((xyz[over] + 0.055) / 1.055) ** 2.4
    xyz[~over] /= 12.92
    xyz = np.dot(xyz, _rgb2xyz_norm)
    over = xyz > 0.008856
    xyz[over] = xyz[over] ** (1. / 3.)
    xyz[~over] = 7.787 * xyz[~over] + 0.13793103448275862

    # Convert XYZ->LAB
    L = (116. * xyz[:, 1]) - 16
    a = 500 * (xyz[:, 0] - xyz[:, 1])
    b = 200 * (xyz[:, 1] - xyz[:, 2])
    labs = [L, a, b]
    # Append alpha if necessary
    if n_dim == 4:
        labs.append(np.atleast1d(rgbs[:, 3]))
    labs = np.array(labs, order='F').T  # Becomes 'C' order b/c of .T
    return labs


def _lab_to_rgb(labs):
    """Convert Nx3 or Nx4 lab to rgb"""
    # adapted from BSD-licensed work in MATLAB by Mark Ruzon
    # Based on ITU-R Recommendation BT.709 using the D65
    labs, n_dim = _check_color_dim(labs)

    # Convert Lab->XYZ (silly indexing used to preserve dimensionality)
    y = (labs[:, 0] + 16.) / 116.
    x = (labs[:, 1] / 500.) + y
    z = y - (labs[:, 2] / 200.)
    xyz = np.concatenate(([x], [y], [z]))  # 3xN
    over = xyz > 0.2068966
    xyz[over] = xyz[over] ** 3.
    xyz[~over] = (xyz[~over] - 0.13793103448275862) / 7.787

    # Convert XYZ->LAB
    rgbs = np.dot(_xyz2rgb_norm, xyz).T
    over = rgbs > 0.0031308
    rgbs[over] = 1.055 * (rgbs[over] ** (1. / 2.4)) - 0.055
    rgbs[~over] *= 12.92
    if n_dim == 4:
        rgbs = np.concatenate((rgbs, labs[:, 3]), axis=1)
    rgbs = np.clip(rgbs, 0., 1.)
    return rgbs


###############################################################################
# Color Array

class ColorArray(object):
    """An array of colors

    Parameters
    ----------
    color : str | tuple | list of colors
        If str, can be any of the names in ``vispy.color.get_color_names``.
        Can also be a hex value if it starts with ``'#'`` as ``'#ff0000'``.
        If array-like, it must be an Nx3 or Nx4 array-like object.
        Can also be a list of colors, such as
        ``['red', '#00ff00', ColorArray('blue')]``.
    alpha : float | None
        If no alpha is not supplied in ``color`` entry and ``alpha`` is None,
        then this will default to 1.0 (opaque). If float, it will override
        any alpha values in ``color``, if provided.

    Examples
    --------
    There are many ways to define colors. Here are some basic cases:

        >>> from vispy.color import ColorArray
        >>> r = ColorArray('red')  # using string name
        >>> r
        <ColorArray: 1 color ((1.0, 0.0, 0.0, 1.0))>
        >>> g = ColorArray((0, 1, 0, 1))  # RGBA tuple
        >>> b = ColorArray('#0000ff')  # hex color
        >>> w = ColorArray()  # defaults to black
        >>> w.rgb = r.rgb + g.rgb + b.rgb
        >>> w == ColorArray('white')
        True
        >>> w.alpha = 0
        >>> w
        <ColorArray: 1 color ((1.0, 1.0, 1.0, 0.0))>
        >>> rgb = ColorArray(['r', (0, 1, 0), '#0000FFFF'])
        >>> rgb
        <ColorArray: 3 colors ((1.0, 0.0, 0.0, 1.0) ... (1.0, 0.0, 0.0, 1.0))>
        >>> rgb == ColorArray(['red', '#00ff00', ColorArray('blue')])
        True

    Notes
    -----
    Under the hood, this class stores data in RGBA format suitable for use
    on the GPU.
    """
    def __init__(self, color='black', alpha=None, clip=False):
        """Parse input type, and set attribute"""
        rgba = _user_to_rgba(color, clip=clip)
        if alpha is not None:
            rgba[:, 3] = alpha
        self._rgba = None
        self.rgba = rgba

    ###########################################################################
    # Builtins and utilities
    def copy(self):
        """Return a copy"""
        return deepcopy(self)

    @classmethod
    def _name(cls):
        """Helper to get the class name once it's been created"""
        return cls.__name__

    def __len__(self):
        return self._rgba.shape[0]

    def __repr__(self):
        nice_str = str(tuple(self._rgba[0]))
        plural = ''
        if len(self) > 1:
            plural = 's'
            nice_str += ' ... ' + str(tuple(self.rgba[-1]))
        # use self._name() here instead of hard-coding name in case
        # we eventually subclass this class
        return ('<%s: %i color%s (%s)>' % (self._name(), len(self),
                                           plural, nice_str))

    def __eq__(self, other):
        return np.array_equal(self._rgba, other._rgba)

    ###########################################################################
    def __getitem__(self, item):
        if isinstance(item, tuple):
            raise ValueError('ColorArray indexing is only allowed along '
                             'the first dimension.')
        subrgba = self._rgba[item]
        if subrgba.ndim == 1:
            assert len(subrgba) == 4
        elif subrgba.ndim == 2:
            assert subrgba.shape[1] in (3, 4)
        return ColorArray(subrgba)

    def __setitem__(self, item, value):
        if isinstance(item, tuple):
            raise ValueError('ColorArray indexing is only allowed along '
                             'the first dimension.')
        # value should be a RGBA array, or a ColorArray instance
        if isinstance(value, ColorArray):
            value = value.rgba
        self._rgba[item] = value

    # RGB(A)
    @property
    def rgba(self):
        """Nx4 array of RGBA floats"""
        return self._rgba.copy()

    @rgba.setter
    def rgba(self, val):
        """Set the color using an Nx4 array of RGBA floats"""
        # Note: all other attribute sets get routed here!
        # This method is meant to do the heavy lifting of setting data
        rgba = _user_to_rgba(val, expand=False)
        if self._rgba is None:
            self._rgba = rgba  # only on init
        else:
            self._rgba[:, :rgba.shape[1]] = rgba

    @property
    def rgb(self):
        """Nx3 array of RGB floats"""
        return self._rgba[:, :3].copy()

    @rgb.setter
    def rgb(self, val):
        """Set the color using an Nx3 array of RGB floats"""
        self.rgba = val

    @property
    def RGBA(self):
        """Nx4 array of RGBA uint8s"""
        return (self._rgba * 255).astype(np.uint8)

    @RGBA.setter
    def RGBA(self, val):
        """Set the color using an Nx4 array of RGBA uint8 values"""
        # need to convert to normalized float
        val = np.atleast_1d(val).astype(np.float32) / 255
        self.rgba = val

    @property
    def RGB(self):
        """Nx3 array of RGBA uint8s"""
        return np.round(self._rgba[:, :3] * 255).astype(int)

    @RGB.setter
    def RGB(self, val):
        """Set the color using an Nx3 array of RGB uint8 values"""
        # need to convert to normalized float
        val = np.atleast_1d(val).astype(np.float32) / 255.
        self.rgba = val

    @property
    def alpha(self):
        """Length-N array of alpha floats"""
        return self._rgba[:, 3]

    @alpha.setter
    def alpha(self, val):
        """Set the color using alpha"""
        self._rgba[:, 3] = _array_clip_val(val)

    ###########################################################################
    # HEX
    @property
    def hex(self):
        """Numpy array with N elements, each one a hex triplet string"""
        return _rgb_to_hex(self._rgba)

    @hex.setter
    def hex(self, val):
        """Set the color values using a list of hex strings"""
        self.rgba = _hex_to_rgba(val)

    ###########################################################################
    # HSV
    @property
    def hsv(self):
        """Nx3 array of HSV floats"""
        return self._hsv

    @hsv.setter
    def hsv(self, val):
        """Set the color values using an Nx3 array of HSV floats"""
        self.rgba = _hsv_to_rgb(val)

    @property
    def _hsv(self):
        """Nx3 array of HSV floats"""
        # this is done privately so that overriding functions work
        return _rgb_to_hsv(self._rgba[:, :3])

    @property
    def value(self):
        """Length-N array of color HSV values"""
        return self._hsv[:, 2]

    @value.setter
    def value(self, val):
        """Set the color using length-N array of (from HSV)"""
        hsv = self._hsv
        hsv[:, 2] = _array_clip_val(val)
        self.rgba = _hsv_to_rgb(hsv)

    def lighter(self, dv=0.1, copy=True):
        """Produce a lighter color (if possible)

        Parameters
        ----------
        dv : float
            Amount to increase the color value by.
        copy : bool
            If False, operation will be carried out in-place.

        Returns
        -------
        color : instance of ColorArray
            The lightened Color.
        """
        color = self.copy() if copy else self
        color.value += dv
        return color

    def darker(self, dv=0.1, copy=True):
        """Produce a darker color (if possible)

        Parameters
        ----------
        dv : float
            Amount to decrease the color value by.
        copy : bool
            If False, operation will be carried out in-place.

        Returns
        -------
        color : instance of ColorArray
            The darkened Color.
        """
        color = self.copy() if copy else self
        color.value -= dv
        return color

    ###########################################################################
    # Lab
    @property
    def lab(self):
        return _rgb_to_lab(self._rgba[:, :3])

    @lab.setter
    def lab(self, val):
        self.rgba = _lab_to_rgb(val)


class LinearGradient(ColorArray):
    """Class to represent linear gradients

    Parameters
    ----------
    colors : ColorArray
        The control points to use as colors.
    x : array
        Array of the same length as ``colors`` that give the x-values
        to use along the axis of the array. By default, it is ``np.arange(n)``
        where ``n = len(colors)``.
    """
    def __init__(self, colors, x=None):
        ColorArray.__init__(self, colors)
        if x is None:
            x = np.arange(len(colors))
        self.gradient_x = x

    @property
    def gradient_x(self):
        return self._grad_x.copy()

    @gradient_x.setter
    def gradient_x(self, val):
        x = np.array(val, dtype=np.float32)
        if x.ndim != 1 or x.size != len(self):
            raise ValueError('x must 1D with the same size as colors (%s), '
                             'not %s' % (len(self), x.shape))
        self._grad_x = x

    def __getitem__(self, loc):
        try:
            loc = float(loc)
        except:
            raise RuntimeError('location could not be converted to float: %s'
                               % str(loc))
        rgba = [np.interp(loc, self._grad_x, rr) for rr in self._rgba.T]
        return np.array(rgba)


class Color(ColorArray):
    """A single color

    Parameters
    ----------
    color : str | tuple
        If str, can be any of the names in ``vispy.color.get_color_names``.
        Can also be a hex value if it starts with ``'#'`` as ``'#ff0000'``.
        If array-like, it must be an 1-dimensional array with 3 or 4 elements.
    alpha : float | None
        If no alpha is not supplied in ``color`` entry and ``alpha`` is None,
        then this will default to 1.0 (opaque). If float, it will override
        the alpha value in ``color``, if provided.
    """
    def __init__(self, color='black', alpha=None, clip=False):
        """Parse input type, and set attribute"""
        if isinstance(color, (list, tuple)):
            color = np.array(color, np.float32)
        rgba = _user_to_rgba(color, clip=clip)
        if rgba.shape[0] != 1:
            raise ValueError('color must be of correct shape')
        if alpha is not None:
            rgba[:, 3] = alpha
        self._rgba = None
        self.rgba = rgba.ravel()

    @ColorArray.rgba.getter
    def rgba(self):
        return super(Color, self).rgba[0]

    @ColorArray.rgb.getter
    def rgb(self):
        return super(Color, self).rgb[0]

    @ColorArray.RGBA.getter
    def RGBA(self):
        return super(Color, self).RGBA[0]

    @ColorArray.RGB.getter
    def RGB(self):
        return super(Color, self).RGB[0]

    @ColorArray.alpha.getter
    def alpha(self):
        return super(Color, self).alpha[0]

    @ColorArray.hex.getter
    def hex(self):
        return super(Color, self).hex[0]

    @ColorArray.hsv.getter
    def hsv(self):
        return super(Color, self).hsv[0]

    @ColorArray.value.getter
    def value(self):
        return super(Color, self).value[0]

    @ColorArray.lab.getter
    def lab(self):
        return super(Color, self).lab[0]

    def is_blank(self):
        return self.rgba[3] == 0

    def __repr__(self):
        nice_str = str(tuple(self._rgba[0]))
        return ('<%s: %s>' % (self._name(), nice_str))


###############################################################################
# Color maps


def _vector_or_scalar(x, type='row'):
    """Convert an object to either a scalar or a row or column vector."""
    if isinstance(x, (list, tuple)):
        x = np.array(x)
    if isinstance(x, np.ndarray):
        assert x.ndim == 1
        if type == 'column':
            x = x[:, None]
    return x


def mix(a, b, x):
    """Mix b (with proportion x) with a."""
    x = np.clip(x, 0.0, 1.0)
    return (1.0 - x)*a + x*b


def smoothstep(a, b, x):
    """Perform smooth Hermite interpolation between 0 and 1 when
    edge0 < x < edge1."""
    # Scale, bias and saturate x to 0..1 range
    x = np.clip((x - a)/(b - a), 0.0, 1.0)
    # Evaluate polynomial
    return x*x*(3 - 2*x)


def _process_glsl_template(template, colors):
    """Replace $color_i by color #i in the GLSL template."""
    for i in range(len(colors)):
        color = colors[i]
        assert len(color) == 4
        vec4_color = 'vec4(%.3f, %.3f, %.3f, %.3f)' % tuple(color)
        template = template.replace('$color_%d' % i, vec4_color)
    return template


class Colormap(ColorArray):
    """Class representing a colormap. Can be used to generate colors from
    scalar values, either on the CPU with NumPy, or on the GPU with texture
    lookup or by generating mathematically the colors in GLSL."""

    """Control colors used by the colormap."""
    colors = None

    """Interpolation function."""
    interpolation = None

    """GLSL string with a function implementing the color map."""
    glsl_map = None

    def __init__(self, colors=None, interpolation=None,
                 glsl_map=None):
        """Create a colormap.

        Parameters
        ----------
        colors : list of ndarray
            The control colors used by the colormap (shape = (4,)).
        interpolation : function or string
            A function that takes (a, b, t) as input and returns a vector
            of same size as a and b (arrays with 4 elements).
            t is expected to be a column vector.
            If a string, one of 'mix' or 'smoothstep'.
        glsl_map : string
            The GLSL function for the colormap. Use $color_0 to refer
            to the first color in `colors`, and so on. These are vec4 vectors.

        """
        # Ensure the colors are either scalars or vectors.
        if colors is not None:
            self.colors = colors
        if self.colors is not None:
            self.colors = [_vector_or_scalar(color) for color in self.colors]

        self.interpolation = (self.interpolation
                              if interpolation is None else interpolation)

        # Default interpolation function is mix.
        if self.interpolation is None:
            self.interpolation = 'mix'

        self.glsl_map = self.glsl_map if glsl_map is None else glsl_map

        # Generate a default GLSL map, assuming the interpolation function
        # is a string.
        if self.glsl_map is None:
            assert isinstance(self.interpolation, string_types)
            self.glsl_map = """
                vec4 %s(float t) {
                    return %s($color_0, $color_1, t);
                }""" % (self.__class__.__name__.lower(),  # colormap name
                        self.interpolation)  # interpolation function name

        # Replace the template variables in the GLSL function.
        if self.colors is not None:
            self.glsl_map = _process_glsl_template(self.glsl_map, self.colors)

        # If interpolation is a string, it's a function name that should
        # be available in the global namespace.
        if isinstance(self.interpolation, string_types):
            self.interpolation = globals()[self.interpolation]

    def map(self, item):
        """Return a rgba array for the requested items. By default,
        apply the interpolation function on (colors[0], colors[1], item).

        This function can be overriden by child classes.

        This function doesn't need to implement argument checking on `item`.

        Parameters
        ----------
        item : ndarray
            An array of values in [0,1]. Expected to be a column vector.

        Returns
        -------
        rgba : ndarray
            A (N, 4) array with rgba values, where N is `len(item)`."""
        return self.interpolation(self.colors[0], self.colors[1], item)

    def __getitem__(self, item):
        if isinstance(item, tuple):
            raise ValueError('ColorArray indexing is only allowed along '
                             'the first dimension.')
        # Ensure item is either a scalar or a column vector.
        item = _vector_or_scalar(item, type='column')
        colors = self.map(item)
        return ColorArray(colors)

    def __setitem__(self, item, value):
        raise RuntimeError("It is not possible to set items to "
                           "Colormap instances.")


class Fire(Colormap):
    colors = [(1.0, 1.0, 1.0, 1.0),
              (1.0, 1.0, 0.0, 1.0),
              (1.0, 0.0, 0.0, 1.0)]

    glsl_map = """
    vec4 fire(float t) {
        return mix(mix($color_0, $color_1, t),
                   mix($color_1, $color_2, t*t), t);
    }
    """

    def map(self, t):
        a, b, d = self.colors
        c = mix(a, b, t)
        e = mix(b, d, t**2)
        return mix(c, e, t)


class Grays(Colormap):
    glsl_map = """
    vec4 grays(float t) {
        return vec4(t, t, t, 1.0);
    }
    """

    def map(self, t):
        return np.array([t, t, t, 1.0], np.float32)


class Ice(Colormap):
    glsl_map = """
    vec4 ice(float t) {
        return vec4(t,t,1.0,1.0);
    }
    """

    def map(self, t):
        return np.array([t, t, 1.0, 1.0], np.float32)


class Hot(Colormap):
    colors = [(0., .33, .66, 1.0),
              (.33, .66, 1., 1.0)]

    glsl_map = """
    vec4 hot(float t) {
        return vec4(smoothstep($color_0.rgb, $color_1.rgb, vec3(t, t, t)),
                    1.0);
    }
    """

    def map(self, t):
        return smoothstep(self.colors[0], self.colors[1], t)


class Winter(Colormap):
    colors = [(0.0, 0.0, 1.0, 1.0),
              (0.0, 1.0, 0.5, 1.0)]

    glsl_map = """
    vec4 winter(float t) {
        return mix($color_0, $color_1, sqrt(t));
    }
    """

    def map(self, t):
        return mix(self.colors[0], self.colors[1], np.sqrt(t))


_colormaps = dict(
    autumn=Colormap([(1., 0., 0., 1.), (1., 1., 0., 1.)]),
    blues=Colormap([(1., 1., 1., 1.), (0., 0., 1., 1.)]),
    cool=Colormap([(0., 1., 1., 1.), (1., 0., 1., 1.)]),
    greens=Colormap([(1., 1., 1., 1.), (0., 1., 0., 1.)]),
    reds=Colormap([(1., 1., 1., 1.), (1., 0., 0., 1.)]),
    spring=Colormap([(1., 0., 1., 1.), (1., 1., 0., 1.)]),
    summer=Colormap([(0., .5, .4, 1.), (1., 1., .4, 1.)]),
    fire=Fire(),
    grays=Grays(),
    hot=Hot(),
    ice=Ice(),
    winter=Winter(),
)


def get_colormap(name):
    """Return a Colormap instance given its name."""
    return _colormaps[name]


def get_colormaps():
    """Return the list of colormap names."""
    return list(sorted(iterkeys(_colormaps)))
