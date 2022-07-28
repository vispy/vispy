# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" Display markers at different sizes and line thicknessess.
"""

import numpy as np
import vispy.scene as scene
from vispy.scene import visuals
from vispy import app

n = 500
pos = np.zeros((n, 2))
colors = np.ones((n, 4), dtype=np.float32)
radius, theta, dtheta = 1.0, 0.0, 5.5 / 180.0 * np.pi
for i in range(500):
    theta += dtheta
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    r = 10.1 - i * 0.02
    radius -= 0.45
    pos[i] = x/512.+.5, 1.-(y/512.+.5)
pos *= 512


class Canvas(scene.SceneCanvas):

    def __init__(self):
        scene.SceneCanvas.__init__(
            self,
            keys='interactive', size=(512, 512),
            title="Marker demo [press space to change marker]",
            bgcolor='white'
        )
        self.unfreeze()
        self.index = 0
        self.markers = visuals.Markers(scaling=False)
        self.markers.set_data(pos, face_color=(0, 1, 0))
        self.markers.symbol = self.markers.symbols[self.index]
        self.text = visuals.Text(self.markers.symbols[self.index],
                                 pos=(80, 15), font_size=14,
                                 color='black', parent=self.scene)
        self.freeze()

    def on_key_press(self, event):
        if event.text == ' ':
            self.index = (self.index + 1) % (len(self.markers.symbols))
            self.markers.symbol = self.markers.symbols[self.index]
            self.text.text = self.markers.symbols[self.index]
            self.update()


canvas = Canvas()
grid = canvas.central_widget.add_grid()
vb1 = grid.add_view(row=0, col=0)
vb1.add(canvas.markers)

if __name__ == '__main__':
    canvas.show()
    app.run()
