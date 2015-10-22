# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
+---+-------+---+
| 1 |   1   | 2 |
|---+-------+---+
| 3 | Empty |   |
+---+-------+---+
| 3 |   4   | 4 |
+---+-------+---+
"""

import sys

from vispy import scene, app

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 600, 600
canvas.bgcolor = "#efefef"
canvas.show()

grid = canvas.central_widget.add_grid()

# red increases along x axis, green along y axis

widget_top_left = grid.add_widget(row=0, col=0, col_span=2)
widget_top_left.bgcolor = "#000000"
widget_top_left.stretch = (2, 1)

widget_top_right = grid.add_widget(row=0, col=2, row_span=2)
widget_top_right.bgcolor = "#ff0000"

widget_bottom_left = grid.add_widget(row=1, col=0, row_span=2)
widget_bottom_left.bgcolor = "#00ff00"

widget_bottom_right = grid.add_widget(row=2, col=1, col_span=2)
widget_bottom_right.bgcolor = "#ffff00"

if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
