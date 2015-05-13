# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of the plane geometry.
"""

import sys

from vispy import scene
from vispy import visuals
from vispy.geometry import create_plane

canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)

view = canvas.central_widget.add_view()

camera = scene.cameras.TurntableCamera(fov=45, parent=view.scene)
view.camera = camera

vertices, faces, outline = create_plane(width=2,
                                        height=4,
                                        width_segments=4,
                                        height_segments=8,
                                        direction='+y')

plane_f = scene.Mesh(vertices=vertices['position'],
                     faces=faces,
                     vertex_colors=vertices['color'],
                     parent=view.scene)

plane_w1 = scene.Mesh(vertices=vertices['position'],
                      faces=outline,
                      vertex_colors=vertices['color'],
                      mode='lines',
                      parent=view.scene)

transform = visuals.transforms.AffineTransform()
transform.translate((0, 0, 2.5))
plane_w1.transform = transform

vertices, faces, outline = create_plane(width=2,
                                        height=4,
                                        width_segments=4,
                                        height_segments=8,
                                        direction='+z')

plane_w2 = scene.Mesh(vertices=vertices['position'],
                      faces=outline,
                      vertex_colors=vertices['color'],
                      mode='lines',
                      parent=view.scene)

transform = visuals.transforms.AffineTransform()
transform.translate((4.5, 0, 0))
plane_w2.transform = transform

if __name__ == '__main__' and sys.flags.interactive == 0:
    canvas.app.run()
