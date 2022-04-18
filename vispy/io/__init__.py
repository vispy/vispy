# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""Utilities related to data reading, writing, fetching, and generation."""


from os import path as _op

from .datasets import (load_iris, load_crate, load_data_file,  # noqa
                       load_spatial_filters)  # noqa
from .mesh import read_mesh, write_mesh  # noqa
from .image import (read_png, write_png, imread, imsave, _make_png,  # noqa
                    _check_img_lib)  # noqa

_data_dir = _op.join(_op.dirname(__file__), '_data')

__all__ = ['imread', 'imsave', 'load_iris', 'load_crate',
           'load_spatial_filters', 'load_data_file',
           'read_mesh', 'read_png', 'write_mesh',
           'write_png']
