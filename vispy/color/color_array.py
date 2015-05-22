# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division  # just to be safe...

import numpy as np
from copy import deepcopy

from ..ext.six import string_types
from ..util import logger
from ._color_dict import _color_dict
from .color_space import (_hex_to_rgba, _rgb_to_hex, _rgb_to_hsv,  # noqa
                          _hsv_to_rgb, _rgb_to_lab, _lab_to_rgb)  # noqa


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


def _array_clip_val(val):
    """Helper to turn val into array and clip between 0 and 1"""
    val = np.array(val)
    if val.max() > 1 or val.min() < 0:
        logger.warning('value will be clipped between 0 and 1')
    val[...] = np.clip(val, 0, 1)
    return val


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
    clip : bool
        Clip the color value.
    color_space : 'rgb' | 'hsv'
       'rgb' (default) : color tuples are interpreted as (r, g, b) components.
       'hsv' : color tuples are interpreted as (h, s, v) components.

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
        >>>hsv_color = ColorArray(color_space="hsv", color=(0, 0, 0.5))
        >>>hsv_color
        <ColorArray: 1 color ((0.5, 0.5, 0.5, 1.0))>
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
    def __init__(self, color=(0., 0., 0.), alpha=None,
                 clip=False, color_space='rgb'):

        # if color is RGB, then set the default color to black
        color = (0,) * 4 if color is None else color
        if color_space == 'hsv':
            # if the color space is hsv, convert hsv to rgb
            color = _hsv_to_rgb(color)
        elif color_space != 'rgb':
            raise ValueError('color_space should be either "rgb" or'
                             '"hsv", it is ' + color_space)

        # Parse input type, and set attribute"""
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

    def extend(self, colors):
        """Extend a ColorArray with new colors

        Parameters
        ----------
        colors : instance of ColorArray
            The new colors.
        """
        colors = ColorArray(colors)
        self._rgba = np.vstack((self._rgba, colors._rgba))
        return self

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
    clip : bool
        If True, clip the color values.
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

    @property
    def is_blank(self):
        """Boolean indicating whether the color is invisible.
        """
        return self.rgba[3] == 0

    def __repr__(self):
        nice_str = str(tuple(self._rgba[0]))
        return ('<%s: %s>' % (self._name(), nice_str))
