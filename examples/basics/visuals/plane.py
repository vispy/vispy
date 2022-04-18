# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of the plane geometry.
"""

import sys

from vispy import scene, geometry

canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)

view = canvas.central_widget.add_view()

vertices, faces, outline = geometry.create_plane(width=2, height=4,
                                                 width_segments=4,
                                                 height_segments=8,
                                                 direction='+y')

plane = scene.visuals.Plane(width=2, height=4, width_segments=4,
                            height_segments=8, direction='+y',
                            vertex_colors=vertices['color'],
                            edge_color='k',
                            parent=view.scene)

camera = scene.cameras.TurntableCamera(fov=45, azimuth=-45, parent=view.scene)
view.camera = camera

if __name__ == '__main__' and sys.flags.interactive == 0:
    canvas.app.run()
