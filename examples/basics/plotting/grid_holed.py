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
| 3 | Empty | 2 |
+---+-------+---+
| 3 |   4   | 4 |
+---+-------+---+
"""

import sys

from vispy import scene, app

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 600, 600
canvas.bgcolor = "#000000"
canvas.show()

grid = canvas.central_widget.add_grid()

# top_left
grid.add_widget(row=0, col=0, col_span=2, bgcolor="#ffffff")

# top_right
grid.add_widget(row=0, col=2, row_span=2, bgcolor="#dddddd")

# bottom_left
grid.add_widget(row=1, col=0, row_span=2, bgcolor="#444444")


# bottom_right
grid.add_widget(row=2, col=1, col_span=2, bgcolor="#888888")


if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
