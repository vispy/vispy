# -*- coding: utf-8 -*-
# vispy: gallery 2
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Simple use of a grid layout
===========================


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

# This is the top-level widget that will hold three ViewBoxes, which will
# be automatically resized whenever the grid is resized.
grid = canvas.central_widget.add_grid()

widget_left = grid.add_widget(row=0, col=0)
widget_left.bgcolor = "#dd0000"

widget_right = grid.add_widget(row=0, col=1)
widget_right.bgcolor = "#0000dd"

canvas.show()

if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
