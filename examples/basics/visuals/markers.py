# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" Display markers at different sizes and line thicknessess.
"""

import numpy as np

from vispy import app, gloo
from vispy.scene.visuals import Markers, marker_types
from vispy.scene.transforms import STTransform

n = 540
pos = np.zeros((n, 2))
radius, theta, dtheta = 1.0, 0.0, 5.5 / 180.0 * np.pi
for i in range(500):
    theta += dtheta
    x = 256 + radius * np.cos(theta)
    y = 256 + 32 + radius * np.sin(theta)
    r = 10.1 - i * 0.02
    radius -= 0.45
    pos[i] = x, y


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=(512, 512 + 2*32),
                            title="Marker demo [press space to change marker]")
        self.index = 0
        self.scale = 1.
        self.markers = Markers()
        self.markers.set_data(pos)
        self.markers.set_style(marker_types[self.index])

    def on_initialize(self, event):
        # We need to give a transform to our visual
        self.transform = STTransform()
        self.markers._program.vert['transform'] = self.transform.shader_map()
        self.apply_zoom()

    def on_draw(self, event):
        gloo.clear(color='white')
        self.markers.draw()

    def on_mouse_wheel(self, event):
        """Use the mouse wheel to zoom."""
        self.scale *= 1.25 if event.delta[1] > 0 else 0.8
        self.scale = max(min(self.scale, 1e2), 1e-2)
        self.apply_zoom()

    def on_resize(self, event):
        self.apply_zoom()

    def apply_zoom(self):
        gloo.set_viewport(0, 0, *self.size)
        self.transform.scale = (2 * self.scale / self.size[0],
                                2 * self.scale / self.size[1], 1.)
        self.transform.translate = [-1, -1]
        self.update()

    def on_key_press(self, event):
        if event.text == ' ':
            self.index = (self.index + 1) % (len(marker_types))
            self.markers.set_style(marker_types[self.index])
            self.update()

if __name__ == '__main__':
    canvas = Canvas()
    canvas.show()
    app.run()
