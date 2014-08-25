"""
Simple test of SceneCanvas containing a single line entity
as its entire scenegraph.
"""
import numpy as np

from vispy import app
from vispy import scene

canvas = scene.SceneCanvas(size=(800, 600), show=True, keys='interactive')

N = 1000
pos = np.empty((N, 2), np.float32)
pos[:, 0] = np.linspace(50., 750., N)
#
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

lines = []

for i in range(20):
    pos = pos.copy()
    pos[:, 1] = np.random.normal(scale=5, loc=(i+1)*30, size=N)
    line = scene.visuals.Line(pos=pos, color=color, parent=canvas.scene,
                              mode='gl')
    lines.append(line)
    line.transform = scene.transforms.STTransform()


def update(event):
    for line in lines:
        scale = [np.sin(event.elapsed)+2, np.cos(event.elapsed)+2]
        #line.transform = scene.transforms.STTransform(scale=scale)
        line.transform.scale = scale

timer = app.Timer(interval=0.016, connect=update)

import sys
if sys.flags.interactive == 0:
    timer.start()
    app.run()
