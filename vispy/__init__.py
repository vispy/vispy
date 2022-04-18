# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""=====
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

try:
    from .version import version as __version__  # noqa
except ImportError:
    # package is not installed
    pass

from .util import config, set_log_level, keys, sys_info  # noqa
from .util.wrappers import use, test  # noqa


def _get_sg_image_scraper():
    from .util.gallery_scraper import VisPyGalleryScraper
    return VisPyGalleryScraper()
