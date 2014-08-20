# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" 
Demonstrate the use of text in the root scene and a viewbox. Note
how the point size is independent of scaling of viewbox and canvas.
"""

import numpy as np
import vispy
from vispy import scene, gloo
from vispy.scene.visuals import Text

# Create canvas with a viewbox at the lower half
canvas = scene.SceneCanvas()
vb = scene.widgets.ViewBox(parent=canvas.scene, border_color='b')
vb.pos = 1, canvas.size[1] // 2 -1
vb.size = canvas.size[0] - 2, canvas.size[1] // 2 - 2
vb.camera.rect = 0, 0, 1, 1

t1 = Text('Text in root scene (24 pt)', parent=canvas.scene, color='red')
t1.point_size = 24
t1.pos = canvas.size[0] // 2, canvas.size[1] // 3

t2 = Text('Text in viewbox (18 pt)', parent=vb.scene, color='green')
t2.point_size = 18
t2.pos = 0.5, 0.5

# Add a line so you can see translate/scale of camera
N = 1000
linedata = np.empty((N, 2), np.float32)
linedata[:, 0] = np.linspace(0, 1, N)
linedata[:, 1] = np.random.uniform(0.5, 0.1, (N,))
vispy.scene.visuals.LineVisual(pos=linedata, color='#f006', parent=vb.scene)

canvas.show()
canvas.app.run()
