# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""Utilities for Vispy. A collection of modules that are used in
one or more Vispy sub-packages.
"""

from .logs import logger, set_log_level, use_log_level  # noqa
from .config import (config, sys_info, save_config, get_config_keys,  # noqa
                     set_data_dir, _TempDir, _get_args)  # noqa
from .fetching import load_data_file  # noqa
from .frozen import Frozen  # noqa
from . import fonts       # noqa
from . import transforms  # noqa
from .wrappers import use, run_subprocess  # noqa
from .bunch import SimpleBunch  # noqa

from typing import Optional

import numpy as np

# `copy` keyword semantics changed in NumPy 2.0
# this maintains compatibility with older versions
# if/when NumPy 2.0 becomes the minimum version, we can remove this
# we don't worry about early dev versions of NumPy 2.0 (that may or may not have the kwarg) here
# see:
#  https://numpy.org/devdocs/numpy_2_0_migration_guide.html#adapting-to-changes-in-the-copy-keyword
#  https://github.com/scipy/scipy/pull/20172
np_copy_if_needed: Optional[bool] = None
if np.lib.NumpyVersion(np.__version__) < "1.28.0":
    np_copy_if_needed = False
