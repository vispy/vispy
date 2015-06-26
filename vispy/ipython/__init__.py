# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
This module provides the binding between Vispy and IPython in the form of
an IPython extension
"""

# load the two functions that IPython uses to instantiate an extension
# that way, the user only needs to run %load_ext vispy.ipython rather that
# %load_ext vispy.ipython.ipython
from .ipython import load_ipython_extension, unload_ipython_extension  # noqa
