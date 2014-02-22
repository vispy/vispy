# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Utilities for Vispy. A collection of modules that are used in
one or more Vispy sub-packages.
"""

from .misc import (_TempDir, is_string, parse_command_line_arguments,  # noqa
                   config, sys_info)  # noqa
from ._logging import logger, set_log_level, use_log_level  # noqa
