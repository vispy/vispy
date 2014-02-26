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


def _user_to_rgba(color, alpha=None):
    """Convert colors from user form to RGBA array"""
    if isinstance(color, string_types):
        if color.startswith('#'):
            # hex color
            color = color[1:]
            lc = len(color)
            if lc not in (6, 8):
                raise ValueError('Hex color must have exactly six or eight '
                                 'elements following the # sign')
            color = [int(color[i:i+2], 16) / 255. for i in range(0, lc, 2)]
        else:
            # named color
            if color not in _color_dict:
                raise ValueError('Color "%s" unknown' % color)
            color = _color_dict[color]
        color = np.array(color)
        if color.size == 3:
            color = np.concatenate((color, [1.0]))
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
    if color.min() < 0 or color.max() > 1:
        logger.warn('Color will be clamped between 0 and 1: %s' % color)
        color = np.clip(color, 0, 1)
    if color.shape[1] not in (3, 4):
        raise ValueError('color must have three or four elements')
    if color.shape[1] == 3:
        color = np.concatenate((color, np.ones((color.shape[0], 1))),
                               axis=1)
    if alpha is not None:
        color[:, 3] = alpha
    return color


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
        return (self._rgba[:, :3] * 255).astype(int)

    @RGB.setter
    def RGB(self, val):
        # need to convert to normalized float
        val = np.atleast_1d(val).astype(np.float64) / 255
        return self._set_rgba(val)

    @property
    def alpha(self):
        return self._rgba[:, 3]

    @alpha.setter
    def alpha(self, val):
        self._rgba[:, 3] = val

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
            nice_str += '... ' + str(tuple(self.rgba[-1]))
        return ('<Color: %i color%s (%s)>' % (len(self), plural, nice_str))

    def __eq__(self, other):
        return np.array_equal(self._rgba, other._rgba)


# This is used by color functions to translate user strings to colors
_color_dict = dict(black=(0, 0, 0),
                   white=(1, 1, 1),
                   gray=(0.5, 0.5, 0.5),
                   r=(1, 0, 0),
                   g=(0, 1, 0),
                   b=(0, 0, 1),
                   red=(1, 0, 0),
                   green=(0, 1, 0),
                   blue=(0, 0, 1),
                   )
