# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""The dpi module enables querying the OS for the screen DPI."""

import sys

__all__ = ['get_dpi']

if sys.platform.startswith('linux'):
    from ._linux import get_dpi
elif sys.platform == 'darwin':
    from ._quartz import get_dpi
elif sys.platform.startswith('win'):
    from ._win32 import get_dpi  # noqa, analysis:ignore
else:
    raise NotImplementedError('unknown system %s' % sys.platform)
