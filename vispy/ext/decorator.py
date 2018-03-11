# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Handle loading decorator package from system or from the bundled copy
"""

try:
    from ._bundled.decorator import *  # noqa
except ImportError:
    from decorator import *  # noqa
