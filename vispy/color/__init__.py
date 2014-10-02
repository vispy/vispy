# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Convience interfaces to manipulate colors.

This module provides support for manipulating colors.
"""

<<<<<<< HEAD
__all__ = ['Color', 'ColorArray', 'Colormap',
           'get_colormap', 'get_colormaps',
           'get_color_names', 'get_color_dict']

from ._color_dict import get_color_names, get_color_dict  # noqa
from .color_array import Color, ColorArray
from .colormap import (Colormap,  # noqa
                       get_colormap, get_colormaps)  # noqa
=======
__all__ = ['Color', 'ColorArray', 'LinearGradient', 'get_color_names',
           'get_colormap_py']

from ._color_dict import get_color_names  # noqa
from ._color import (Color, ColorArray, LinearGradient,  # noqa
                     get_colormap, colormaps, get_colormap_py)  # noqa
>>>>>>> new visuals/isocurve for tri mesh
