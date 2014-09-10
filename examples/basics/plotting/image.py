# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Example of simple image plotting.
"""

import sys
import numpy as np

import vispy.plot as vp

canvas = vp.image(np.random.normal(128, 60, (20, 20)).astype(np.ubyte))

# Start up the event loop if this is not an interactive prompt.
if __name__ == '__main__' and sys.flags.interactive == 0:
    canvas.app.run()
