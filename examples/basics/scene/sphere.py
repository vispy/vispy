# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

"""
This example demonstrates how to create a sphere.
"""

import sys

from vispy import scene
canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)

view = canvas.central_widget.add_view()
view.camera = 'arcball'
view.padding = 100

sphere = scene.visuals.Sphere(radius=1, parent=view.scene,
                              edge_color='black')

if __name__ == '__main__' and sys.flags.interactive == 0:
    canvas.app.run()
