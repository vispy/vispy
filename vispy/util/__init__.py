# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Utilities for Vispy. A collection of modules that are used in
one or more Vispy sub-packages.
"""

from .misc import (parse_command_line_arguments, config)  # noqa
from ._logging import logger, set_log_level, use_log_level  # noqa
from ._testing import (_TempDir, sys_info, assert_in, assert_not_in,  # noqa
                       assert_is, app_opengl_context)  # noqa
from ._data import get_data_file  # noqa
