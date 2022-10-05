# -*- coding: utf-8 -*-
# vispy: gallery 2
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Vertical bar plot with Axis 
===========================
"""

import numpy as np
from vispy import scene, app

if __name__ == "__main__":

    canvas = scene.SceneCanvas(keys='interactive', vsync=False)
    canvas.size = 800, 600
    canvas.show()

    grid = canvas.central_widget.add_grid()
    grid.padding = 10

    vb1 = grid.add_view(row=0, col=1, camera='panzoom')

    x_axis1 = scene.AxisWidget(orientation='bottom')
    x_axis1.stretch = (1, 0.1)
    grid.add_widget(x_axis1, row=1, col=1)
    x_axis1.link_view(vb1)
    y_axis1 = scene.AxisWidget(orientation='left')
    y_axis1.stretch = (0.1, 1)
    grid.add_widget(y_axis1, row=0, col=0)
    y_axis1.link_view(vb1)

    grid_lines1 = scene.visuals.GridLines(parent=vb1.scene)

    color_array = np.array([[1,0,0], [0,1,0], [0, 0, 1], [0.5, 1, 0.25], [1, 0.5, 0.25], [0.25, 0.5, 1], [1,0,0], [0,1,0], [0, 0, 1], [0.5, 1, 0.25], [1, 0.5, 0.25], [0.25, 0.5, 1]])

    bar1 = scene.Bar(height=np.arange(0, 6, 0.5),  # for a more traditional horizontal plot, either remove the 
                     bottom=np.arange(0, 3, 0.25), width=0.8, shift=0.5,  # orientation paramenter outright
                     orientation='v', color=color_array, parent=vb1.scene)  # or set it to 'h'

    vb1.camera.set_range()
    
    app.run()
