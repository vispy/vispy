# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" Display markers at different sizes and line thicknessess.
"""

import numpy as np

from vispy import app, gloo, visuals
from vispy.visuals.transforms import STTransform, TransformSystem

n = 500
pos = np.zeros((n, 2))
colors = np.ones((n, 4), dtype=np.float32)
radius, theta, dtheta = 1.0, 0.0, 5.5 / 180.0 * np.pi
for i in range(500):
    theta += dtheta
    x = 256 + radius * np.cos(theta)
    y = 256 + radius * np.sin(theta)
    r = 10.1 - i * 0.02
    radius -= 0.45
    pos[i] = x, y
    colors[i] = (i/500, 1.0-i/500, 0, 1)


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=(512, 512),
                            title="Marker demo [press space to change marker]")
        self.index = 0
        self.scale = 1.
        self.tr_sys = TransformSystem(self)
        self.tr_sys.visual_to_document = STTransform()
        self.markers = visuals.MarkersVisual()
        self.markers.set_data(pos, face_color=colors)
        self.markers.set_symbol(visuals.marker_types[self.index])

        self.show()

    def on_draw(self, event):
        gloo.clear(color='white')
        self.markers.draw(self.tr_sys)

    def on_mouse_wheel(self, event):
        """Use the mouse wheel to zoom."""
        self.scale *= 1.25 if event.delta[1] > 0 else 0.8
        self.scale = max(min(self.scale, 1e2), 1e-2)
        self.apply_zoom()

    def on_resize(self, event):
        self.apply_zoom()

    def apply_zoom(self):
        gloo.set_viewport(0, 0, *self.physical_size)
        self.tr_sys.visual_to_document.scale = (self.scale, self.scale)
        self.update()

    def on_key_press(self, event):
        if event.text == ' ':
            self.index = (self.index + 1) % (len(visuals.marker_types))
            self.markers.set_symbol(visuals.marker_types[self.index])
            self.update()

if __name__ == '__main__':
    canvas = Canvas()
    app.run()
