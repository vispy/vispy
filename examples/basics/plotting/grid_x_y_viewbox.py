

# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""
+----+-------------+
|    |             |
| y  |   viewbox   |
|    |             |
+----+-------------+
| sp |     x       |
+----+-------------+
"""

import sys

from vispy import scene, app

canvas = scene.SceneCanvas(keys='interactive')
canvas.size = 600, 600
canvas.show()

grid = canvas.central_widget.add_grid()

widget_y_axis = grid.add_widget(row=0, col=0)
widget_y_axis.bgcolor = "#999999"

widget_viewbox = grid.add_widget(row=0, col=1)
widget_viewbox.bgcolor = "#dd0000"

widget_spacer_bottom = grid.add_widget(row=1, col=0)
widget_spacer_bottom.bgcolor = "#efefef"

widget_x_axis = grid.add_widget(row=1, col=1)
widget_x_axis.bgcolor = "#0000dd"

widget_y_axis.width_min = 50
widget_y_axis.width_max = 50
widget_x_axis.height_min = 50
widget_x_axis.height_max = 50

if __name__ == '__main__' and sys.flags.interactive == 0:
    app.run()
