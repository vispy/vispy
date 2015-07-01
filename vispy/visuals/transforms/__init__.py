# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Provides classes representing different transform types suitable for
use with visuals and scenes.
"""


from .base_transform import BaseTransform  # noqa
from .linear import (NullTransform, STTransform,  # noqa
                     MatrixTransform,  MatrixTransform)  # noqa
from .nonlinear import LogTransform, PolarTransform  # noqa
from .interactive import PanZoomTransform
from .chain import ChainTransform  # noqa
from ._util import arg_to_array, arg_to_vec4, as_vec4, TransformCache  # noqa
from .transform_system import TransformSystem

__all__ = ['NullTransform', 'STTransform', 'MatrixTransform',
           'MatrixTransform', 'LogTransform', 'PolarTransform',
           'ChainTransform', 'TransformSystem', 'PanZoomTransform']

transform_types = {}
for o in list(globals().values()):
    try:
        if issubclass(o, BaseTransform) and o is not BaseTransform:
            name = o.__name__[:-len('Transform')].lower()
            transform_types[name] = o
    except TypeError:
        continue


def create_transform(type, *args, **kwargs):
    return transform_types[type](*args, **kwargs)
