# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

__all__ = ['crate', 'read_mesh', 'write_mesh', 'imread', 'imsave',
           'read_png', 'load_iris', 'cube', 'make_png', 'get_data_file']

from os import path as _op

from .cube import cube  # noqa
from .datasets import load_iris  # noqa
from ..util.fetching import get_data_file  # noqa
from .io import (crate, read_mesh, write_mesh, imread, imsave,  # noqa
                 read_png, _check_img_lib)  # noqa
from .image import make_png  # noqa

vispy_data_dir = _op.join(_op.dirname(__file__), '_data')
