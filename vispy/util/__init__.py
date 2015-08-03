# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Utilities for Vispy. A collection of modules that are used in
one or more Vispy sub-packages.
"""

from .logs import logger, set_log_level, use_log_level  # noqa
from .config import (config, sys_info, save_config, get_config_keys,  # noqa 
                     set_data_dir, _TempDir)  # noqa
from .fetching import load_data_file  # noqa
from .frozen import Frozen  # noqa
from . import fonts       # noqa
from . import transforms  # noqa
from .wrappers import use, run_subprocess  # noqa
from .bunch import SimpleBunch  # noqa
