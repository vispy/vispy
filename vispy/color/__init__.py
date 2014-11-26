# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Convience interfaces to manipulate colors.

This module provides support for manipulating colors.
"""

__all__ = ['Color', 'ColorArray', 'LinearGradient', 'Colormap',
           'Autumn',
           'get_color_names', 'get_color_dict']

from ._color_dict import get_color_names, get_color_dict  # noqa
from ._color import (Color, ColorArray, LinearGradient, Colormap,  # noqa
                     Autumn,  # noqa
                     get_colormap, colormaps)  # noqa
