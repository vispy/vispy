# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Provides classes representing different transform types suitable for
use with visuals and scenes.
"""

__all__ = ['NullTransform', 'STTransform', 'AffineTransform',
           'PerspectiveTransform', 'LogTransform', 'PolarTransform',
           'ChainTransform']

from .base_transform import BaseTransform  # noqa
from .linear import (NullTransform, STTransform,  # noqa
                     AffineTransform,  PerspectiveTransform)  # noqa
from .nonlinear import LogTransform, PolarTransform  # noqa
from .chain import ChainTransform  # noqa
from ._util import arg_to_array, arg_to_vec4, TransformCache  # noqa


transform_types = {}
for o in list(globals().values()):
    try:
        if issubclass(o, BaseTransform) and o is not BaseTransform:
            name = o.__name__[:-len('Transform')].lower()
            transform_types[name] = o
    except TypeError:
        continue


def create_transform(type, *args, **kwds):
    return transform_types[type](*args, **kwds)
