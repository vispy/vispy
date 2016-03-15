# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Show a simple use of grids to setup layouts


+-----+-----+
|     |     |
|  1  |  2  |
|     |     |
+-----+-----+
"""

import sys

from vispy import scene, app

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 600, 600
canvas.show()

# This is the top-level widget that will hold three ViewBoxes, which will
# be automatically resized whenever the grid is resized.
grid = canvas.central_widget.add_grid()

widget_left = grid.add_widget(row=0, col=0)
widget_left.bgcolor = "#dd0000"

widget_right = grid.add_widget(row=0, col=1)
widget_right.bgcolor = "#0000dd"


if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
