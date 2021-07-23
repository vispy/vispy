# -*- coding: utf-8 -*-
# vispy: gallery 2
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Another Grid Layout
===================

+-----+-----+-----+
|  1  |  2  |  2  |
+-----+-----+-----+
|  3  |  3  |  4  |
+-----+-----+-----+
"""

import sys

from vispy import scene, app

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 600, 600
canvas.show()

grid = canvas.central_widget.add_grid()

# top_left
grid.add_widget(row=0, col=0, bgcolor="#999999")

# top_right
grid.add_widget(row=0, col=1, col_span=2, bgcolor="#dd0000")

# bottom_left
grid.add_widget(row=1, col=0, col_span=2, bgcolor="#0000dd")

# bottom_right
grid.add_widget(row=1, col=2, bgcolor="#00dd00")


if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
