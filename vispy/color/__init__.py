# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Convience interfaces to manipulate colors.

This module provides support for manipulating colors.
"""

__all__ = ['Color', 'ColorArray', 'LinearGradient', 'get_color_names']

from ._color_dict import get_color_names  # noqa
from ._color import Color, ColorArray, LinearGradient  # noqa
