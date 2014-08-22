# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Utilities for Vispy. A collection of modules that are used in
one or more Vispy sub-packages.
"""

from .logs import logger, set_log_level, use_log_level  # noqa
from .config import (_parse_command_line_arguments, config, sys_info,  # noqa
                     save_config, get_config_keys, set_data_dir,  # noqa
                     _TempDir)  # noqa

from . import fonts       # noqa
from . import transforms  # noqa
from .wrappers import test, use, run_subprocess  # noqa
