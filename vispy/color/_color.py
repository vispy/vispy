# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division  # just to be safe...

import numpy as np
from os import path as op
import json
from copy import deepcopy

from ..util.six import string_types
from ..util import logger


###############################################################################
# User-friendliness helpers

def get_color_names():
    """Get the known color names

    Returns
    -------
    names : list
        List of color names known by vispy.
    """
    return list(_color_dict.keys())


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


def _user_to_rgba(color, expand=True):
    """Convert color(s) from any set of fmts (str/hex/arr) to RGB(A) array"""
    if isinstance(color, string_types):
        color = _string_to_rgb(color)
    elif isinstance(color, ColorArray):
        color = color.rgba
    # We have to treat this specially
    elif isinstance(color, (list, tuple)):
        if any(isinstance(c, string_types) for c in color):
            color = [_user_to_rgba(c) for c in color]
            if any(len(c) > 1 for c in color):
                raise RuntimeError('could not parse colors, are they nested?')
            color = [c[0] for c in color]
    color = np.atleast_2d(color).astype(np.float64)
    if color.shape[1] not in (3, 4):
        raise ValueError('color must have three or four elements')
    if expand and color.shape[1] == 3:  # only expand if requested
        color = np.concatenate((color, np.ones((color.shape[0], 1))),
                               axis=1)
    if color.min() < 0 or color.max() > 1:
        logger.warn('Color will be clamped between 0 and 1: %s' % color)
        color = np.clip(color, 0, 1)
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
        logger.warn('value will be clipped between 0 and 1')
    val[...] = np.clip(val, 0, 1)
    return val


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
    hsvs = np.array(hsvs, dtype=np.float64)
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
    rgbs = np.array(rgbs, dtype=np.float64)
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
# Now for the user-level classes

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
    def __init__(self, color=(0., 0., 0., 1.), alpha=None):
        """Parse input type, and set attribute"""
        rgba = _user_to_rgba(color)
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
        val = np.atleast_1d(val).astype(np.float64) / 255
        self.rgba = val

    @property
    def RGB(self):
        """Nx3 array of RGBA uint8s"""
        return np.round(self._rgba[:, :3] * 255).astype(int)

    @RGB.setter
    def RGB(self, val):
        """Set the color using an Nx3 array of RGB uint8 values"""
        # need to convert to normalized float
        val = np.atleast_1d(val).astype(np.float64) / 255.
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
    # HSV
    @property
    def hsv(self):
        """Nx3 array of HSV floats"""
        return _rgb_to_hsv(self._rgba[:, :3])

    @hsv.setter
    def hsv(self, val):
        """Set the color values using an Nx3 array of HSV floats"""
        self.rgba = _hsv_to_rgb(val)

    @property
    def value(self):
        """Length-N array of color HSV values"""
        return self.hsv[:, 2]

    @value.setter
    def value(self, val):
        """Set the color using length-N array of (from HSV)"""
        hsv = self.hsv
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
        to use along the axis of the array.
    """
    def __init__(self, colors, x):
        ColorArray.__init__(self, colors)
        self.gradient_x = x

    @property
    def gradient_x(self):
        return self._grad_x.copy()

    @gradient_x.setter
    def gradient_x(self, val):
        x = np.array(val, dtype=np.float64)
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


# This is used by color functions to translate user strings to colors
# For now, this is web colors, and all in hex. It will take some simple
# but annoying refactoring to deal with non-hex entries if we want them.
_color_dict = dict(r='#FF0000',
                   g='#00FF00',
                   b='#0000FF',
                   white='#FFFFFF',
                   silver='#C0C0C0',
                   gray='#808080',
                   black='#000000',
                   red='#FF0000',
                   maroon='#800000',
                   yellow='#FFFF00',
                   olive='#808000',
                   lime='#00FF00',
                   green='#008000',
                   aqua='#00FFFF',
                   teal='#008080',
                   blue='#0000FF',
                   navy='#000080',
                   fuchsia='#FF00FF',
                   purple='#800080',
                   )
# Add the CSS colors, courtesy MIT-licensed code from Dave Eddy:
# github.com/bahamas10/css-color-names/blob/master/css-color-names.json
_css_file = op.join(op.dirname(__file__), '..', 'data',
                    'css-color-names.json')
with open(_css_file, 'r') as fid:
    _color_dict.update(json.load(fid))
