# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
The fonts module implements some helpful functions for dealing with system
fonts.
"""

__all__ = ['list_fonts']

from ._triage import _load_glyph, list_fonts  # noqa, analysis:ignore
from ._vispy_fonts import _vispy_fonts  # noqa, analysis:ignore
