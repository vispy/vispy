# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
columns ->
  0     1    2
0 +-----+----+------+
  | 1   |  2 |  2   |
1 +-----+----+------+
  |   3 |  3 |   4  |
2 +-----+----+------+
rows
 |
 v
"""

import sys

from vispy import scene, app

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 600, 600
canvas.show()

grid = canvas.central_widget.add_grid()

widget_top_left = grid.add_widget(row=0, col=0)
widget_top_left.bgcolor = "#999999"

widget_top_right = grid.add_widget(row=0, col=1, col_span=2)
widget_top_right.bgcolor = "#dd0000"

widget_bottom_left = grid.add_widget(row=1, col=0, col_span=2)
widget_bottom_left.bgcolor = "#0000dd"


widget_bottom_right = grid.add_widget(row=1, col=2)
widget_bottom_right.bgcolor = "#00dd00"


if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
