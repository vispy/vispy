# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np

from ..util.six import string_types
from ..util import logger


def get_color_names():
    """Get the known color names

    Returns
    -------
    names : list
        List of color names known by vispy.
    """
    return list(_color_dict.keys())


def _string_to_rgba(color, alpha):
    """Convert user string or hex color to color array"""
    if not color.startswith('#'):
        if color.lower() not in _color_dict:
            raise ValueError('Color "%s" unknown' % color)
        color = _color_dict[color]
        assert color[0] == '#'
    # hex color
    color = color[1:]
    lc = len(color)
    if lc not in (6, 8):
        raise ValueError('Hex color must have exactly six or eight '
                         'elements following the # sign')
    color = [int(color[i:i+2], 16) / 255. for i in range(0, lc, 2)]
    if len(color) == 3:
        alpha = 1.0 if alpha is None else alpha
        color.append(alpha)
    return np.array(color)


def _user_to_rgba(color, alpha=None):
    """Convert color(s) from any set of fmts (str/hex/array) to RGBA array"""
    if isinstance(color, string_types):
        color = _string_to_rgba(color, alpha)
    elif isinstance(color, Color):
        color = color.rgba
    # We have to treat this specially
    elif isinstance(color, (list, tuple)):
        if any(isinstance(c, string_types) for c in color):
            color = [_user_to_rgba(c, alpha) for c in color]
            if any(len(c) > 1 for c in color):
                raise RuntimeError('could not parse colors, are they nested?')
            color = [c[0] for c in color]
    color = np.atleast_2d(color).astype(np.float64)
    if color.shape[1] not in (3, 4):
        raise ValueError('color must have three or four elements')
    if color.shape[1] == 3:
        color = np.concatenate((color, np.ones((color.shape[0], 1))),
                               axis=1)
    if color.min() < 0 or color.max() > 1:
        logger.warn('Color will be clamped between 0 and 1: %s' % color)
        color = np.clip(color, 0, 1)
    if alpha is not None:
        color[:, 3] = alpha
    return color


def _check_color_dim(val):
    """Ensure val is Nx(n_col), usually Nx3"""
    val = np.atleast_2d(val)
    if val.shape[1] not in (3, 4):
        raise RuntimeError('Value must have second dimension of size 3 or 4')
    return val, val.shape[1]


def _rgb_to_hsv(rgbs):
    """Convert Nx3 or Nx4 rgb to hsv"""
    rgbs, n_dim = _check_color_dim(rgbs)
    hsvs = list()
    for rgb in rgbs:
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
        if n_dim == 4:
            hsv.append(rgbs[3])
        hsvs.append(hsv)
    hsvs = np.array(hsvs, dtype=np.float64)
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
        elif 1 <= hp < 2:
            r, g, b = x, c, 0
        elif 2 <= hp < 3:
            r, g, b = 0, c, x
        elif 3 <= hp < 4:
            r, g, b = 0, x, c
        elif 4 <= hp < 5:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        rgb = [r + m, g + m, b + m]
        if n_dim == 4:
            rgb.append(hsvs[3])
        rgbs.append(rgb)
    rgbs = np.array(rgbs, dtype=np.float64)
    return rgbs


class Color(object):
    """A color object

    Parameters
    ----------
    color : str | tuple | list of colors |
        If str, can be any of the names in ``vispy.color.get_color_names``.
        Can also be a hex value if it starts with ``'#'`` as ``'#ff0000'``.
        If array-like, it must be an Nx3 or Nx4 array-like object.
    alpha : float | None
        If no alpha is not supplied in ``color`` entry and ``alpha`` is None,
        then this will default to 1.0 (opaque). If float, it will override
        any alpha values in ``color``, if provided.

    Examples
    --------
    There are many ways to define colors. Here are some basic cases:

        >>> from vispy.color import Color
        >>> r = Color('red')  # using string name
        >>> r
        <Color: 1 color ((1.0, 0.0, 0.0, 1.0))>
        >>> g = Color((0, 1, 0, 1))  # RGBA tuple
        >>> b = Color('#ff0000')  # hex color
        >>> w = Color()  # defaults to black
        >>> w.rgb = r.rgb + g.rgb + b.rgb
        >>> w == Color('white')
        True
        >>> w.alpha = 0
        >>> w
        <Color: 1 color ((1.0, 1.0, 1.0, 0.0))>
        >>> rgb = Color(['r', (0, 1, 0), '#FF0000FF'])
        >>> rgb
        <Color: 3 colors ((1.0, 0.0, 0.0, 1.0) ... (1.0, 0.0, 0.0, 1.0))>
        >>>
    """
    def __init__(self, color=(0., 0., 0., 1.), alpha=None):
        """Parse input type"""
        self._rgba = None
        self.rgba = _user_to_rgba(color, alpha=alpha)

    def _set_rgba(self, val):
        if self._rgba is None:
            self._rgba = val
            return
        self._rgba = _user_to_rgba(val)

    @property
    def rgb(self):
        return self._rgba[:, :3].copy()

    @rgb.setter
    def rgb(self, val):
        self._set_rgba(val)

    @property
    def rgba(self):
        return self._rgba.copy()

    @rgba.setter
    def rgba(self, val):
        return self._set_rgba(val)

    @property
    def RGBA(self):
        return (self._rgba * 255).astype(int)

    @RGBA.setter
    def RGBA(self, val):
        # need to convert to normalized float
        val = np.atleast_1d(val).astype(np.float64) / 255
        return self._set_rgba(val)

    @property
    def RGB(self):
        return np.round(self._rgba[:, :3] * 255).astype(int)

    @RGB.setter
    def RGB(self, val):
        # need to convert to normalized float
        val = np.atleast_1d(val).astype(np.float64) / 255.
        return self._set_rgba(val)

    @property
    def alpha(self):
        return self._rgba[:, 3]

    @alpha.setter
    def alpha(self, val):
        self._rgba[:, 3] = val

    @property
    def hsv(self):
        return _rgb_to_hsv(self._rgba[:, :3])

    @hsv.setter
    def hsv(self, val):
        return self._set_rgba(_hsv_to_rgb(val))

    @property
    def value(self):
        return self.hsv[:, 2]

    @value.setter
    def value(self, val):
        hsv = self.hsv
        val = np.array(val)
        if val.max() > 1 or val.min() < 0:
            logger.warn('value will be clipped between 0 and 1')
        val = np.clip(val, 0, 1)
        hsv[:, 2] = val
        return self._set_rgba(_hsv_to_rgb(hsv))

    def lighten(self):
        """Lighten the color"""
        # we might be able to do something perceptually nicer here...
        self.value = (self.value + 1) / 2

    def darken(self):
        """Darken the color"""
        # we might be able to do something perceptually nicer here...
        self.value /= 2

    def copy(self):
        """Return a copy of the color"""
        return Color(self)

    def __len__(self):
        return self._rgba.shape[0]

    def __repr__(self):
        nice_str = str(tuple(self._rgba[0]))
        plural = ''
        if len(self) > 1:
            plural = 's'
            nice_str += ' ... ' + str(tuple(self.rgba[-1]))
        return ('<Color: %i color%s (%s)>' % (len(self), plural, nice_str))

    def __eq__(self, other):
        return np.array_equal(self._rgba, other._rgba)


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
