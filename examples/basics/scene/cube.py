# -*-coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Simple use of SceneCanvas to display a cube with an arcball camera.
"""
import sys

from vispy import scene
from vispy.visuals.transforms import AffineTransform
from vispy.color import Color
canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)

# Set up a viewbox to display the cube with interactive arcball
view = canvas.central_widget.add_view()
view.bgcolor = '#efefef'
view.camera = 'turntable'

color = Color("#3f51b5")

cube = scene.visuals.Cube(size=0.5, color=color, edge_color="black",
                          parent=view.scene)
cube_transform = AffineTransform()
# cube_transform.rotate(30, (1, 0, 1))
# cube_transform.translate([0.5, 0.5, 0.5])
# cube.transform = cube_transform

if __name__ == '__main__' and sys.flags.interactive == 0:
    canvas.app.run()
