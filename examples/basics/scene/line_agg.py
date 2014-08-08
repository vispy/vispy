"""
Simple test of SceneCanvas containing a single line entity
as its entire scenegraph.
"""
from vispy import app
from vispy.scene.visuals import LineAgg
from vispy.scene import SceneCanvas, LineAgg, ViewBox

import numpy as np

canvas = SceneCanvas(close_keys='escape')

vb = ViewBox(parent=canvas.scene)

@canvas.events.resize.connect
def resize(event):
    global vb, canvas
    vb.size = canvas.size

canvas.size = 600, 600
canvas.show()



x = np.linspace(0, 1, 1000)
y = np.sin(15*x) + 0.5
vertices1 = np.c_[x,y]
vertices2 = np.c_[np.cos(3*x)*.5, np.sin(3*x)*.5]

line = LineAgg(paths=[vertices1, vertices2], style=[
    dict(color=(1., 0., 0., 1.)),
    dict(color=(0., 1., 0., 1.)),
])
vb.add(line)


import sys
if sys.flags.interactive == 0:
    app.run()
