# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Example of simple scatter plotting.
"""

import sys

import vispy.plot as vp

canvas = vp.scatter([(0, 2), (1, 6), (2, 1), (6, 10)])

# Start up the event loop if this is not an interactive prompt.
if __name__ == '__main__' and sys.flags.interactive == 0:
    canvas.app.run()
