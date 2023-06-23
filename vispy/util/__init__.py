# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""Utilities for Vispy. A collection of modules that are used in
one or more Vispy sub-packages.
"""

from .logs import logger, set_log_level, use_log_level
from .config import (
    config,
    sys_info,
    save_config,
    get_config_keys,
    set_data_dir,
    _TempDir,
    _get_args,
)
from .fetching import load_data_file
from .frozen import Frozen
from . import fonts
from . import transforms
from .wrappers import use, run_subprocess
from .bunch import SimpleBunch


__all__ = (
    "logger",
    "set_log_level",
    "use_log_level",
    "config",
    "sys_info",
    "save_config",
    "get_config_keys",
    "set_data_dir",
    "load_data_file",
    "_TempDir",
    "_get_args",
    "load_data_file",
    "Frozen",
    "fonts",
    "transforms",
    "use",
    "run_subprocess",
    "SimpleBunch",
)
