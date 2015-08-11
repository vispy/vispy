# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Handle loading cassowary package from system or from the bundled copy
"""

try:
    from ._bundled import cassowary  # noqa
except ImportError:
    import cassowary  # noqa
