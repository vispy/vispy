# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from .base_transform import BaseTransform  # noqa
from .linear import (NullTransform, STTransform, SRTTransform,  # noqa
                     AffineTransform,  PerspectiveTransform)  # noqa
from .nonlinear import LogTransform, PolarTransform  # noqa
from .chain import ChainTransform  # noqa
from ._util import arg_to_array, arg_to_vec4, TransformCache  # noqa


transform_types = {}
for o in globals().values():
    try:
        if issubclass(o, BaseTransform) and o is not BaseTransform:
            name = o.__name__[:-len('Transform')].lower()
            transform_types[name] = o
    except TypeError:
        continue

def create_transform(type, *args, **kwds):
    return transform_types[type](*args, **kwds)
