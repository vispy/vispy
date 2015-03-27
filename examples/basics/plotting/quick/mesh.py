# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Example of simple mesh plotting and manipulation.
"""

import sys

from vispy.io import load_data_file
import vispy.plot.q as vpq

canvas = vpq.mesh(fname=load_data_file('orig/triceratops.obj.gz'))

if __name__ == '__main__' and sys.flags.interactive == 0:
    canvas.app.run()
