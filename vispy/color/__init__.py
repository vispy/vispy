# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Convience interfaces to manipulate colors.

This module provides support for manipulating colors.
"""

from ._color_dict import get_color_names, get_color_dict  # noqa
from .color_array import Color, ColorArray
from .colormap import (
    Colormap,
    BaseColormap,
    get_colormap,
    get_colormaps,
)  # noqa
from .transfer_function import BaseTransferFunction, TextureSamplingTF  # noqa

__all__ = [
    "Color",
    "ColorArray",
    "Colormap",
    "BaseColormap",
    "BaseTransferFunction",
    "TextureSamplingTF",
    "get_colormap",
    "get_colormaps",
    "get_color_names",
    "get_color_dict",
]
