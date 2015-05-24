# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""

=====
Vispy
=====

Vispy is a **high-performance interactive 2D/3D data visualization
library**. Vispy leverages the computational power of modern **Graphics
Processing Units (GPUs)** through the **OpenGL** library to display very
large datasets.

For more information, see http://vispy.org.

"""

from __future__ import division

__all__ = ['use', 'sys_info', 'set_log_level', 'test']

# Definition of the version number
version_info = 0, 5, 0, 'dev0'  # major, minor, patch, extra

# Nice string for the version (mimic how IPython composes its version str)
__version__ = '-'.join(map(str, version_info)).replace('-', '.').strip('-')

from .util import config, set_log_level, keys, sys_info  # noqa
from .util.wrappers import use  # noqa
from .testing import test  # noqa
