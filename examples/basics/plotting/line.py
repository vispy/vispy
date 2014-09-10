# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Example of simple line plotting.
"""

import sys

import vispy.plot as vp

canvas = vp.plot([1, 6, 2, 4, 3, 8, 4, 6, 5, 2])

# Start up the event loop if this is not an interactive prompt.
if __name__ == '__main__' and sys.flags.interactive == 0:
    canvas.app.run()
