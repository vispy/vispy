# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" Display markers at different sizes and line thicknessess.
"""

import numpy as np

from vispy import app, visuals
from vispy.visuals.transforms import STTransform

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
        self.markers = visuals.MarkersVisual()
        self.markers.set_data(pos, face_color=colors)
        self.markers.symbol = visuals.marker_types[self.index]
        self.markers.transform = STTransform()

        self.show()

    def on_draw(self, event):
        self.context.clear(color='white')
        self.markers.draw()

    def on_mouse_wheel(self, event):
        """Use the mouse wheel to zoom."""
        self.markers.transform.zoom((1.25**event.delta[1],)*2, 
                                    center=event.pos)
        self.update()

    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)
        self.markers.transforms.configure(viewport=vp, canvas=self)

    def on_key_press(self, event):
        if event.text == ' ':
            self.index = (self.index + 1) % (len(visuals.marker_types))
            self.markers.symbol = visuals.marker_types[self.index]
            self.update()
        elif event.text == 's':
            self.markers.scaling = not self.markers.scaling
            self.update()


if __name__ == '__main__':
    canvas = Canvas()
    app.run()
