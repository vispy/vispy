# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
from vispy.util.six import string_types

def is_string(s): return isinstance(s,string_types)
