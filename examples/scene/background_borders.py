# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Demonstration of borders and background colors
==============================================
"""

from vispy.scene import SceneCanvas

canvas = SceneCanvas(keys='interactive', bgcolor='w', show=True)
grid = canvas.central_widget.add_grid(spacing=0, bgcolor='gray',
                                      border_color='k')
view1 = grid.add_view(row=0, col=0, margin=10, bgcolor=(1, 0, 0, 0.5),
                      border_color=(1, 0, 0))
view2 = grid.add_view(row=0, col=1, margin=10, bgcolor=(0, 1, 0, 0.5),
                      border_color=(0, 1, 0))

if __name__ == '__main__':
    canvas.app.run()
