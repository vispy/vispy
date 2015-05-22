# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Convience interfaces to manipulate colors.

This module provides support for manipulating colors.
"""

from ._color_dict import get_color_names, get_color_dict  # noqa
from .color_array import Color, ColorArray
from .colormap import (Colormap, BaseColormap,  # noqa
                       get_colormap, get_colormaps)  # noqa

__all__ = ['Color', 'ColorArray', 'Colormap', 'BaseColormap',
           'get_colormap', 'get_colormaps',
           'get_color_names', 'get_color_dict']
