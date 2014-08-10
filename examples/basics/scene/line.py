"""
Simple test of SceneCanvas containing a single line entity
as its entire scenegraph.
"""
import numpy as np

from vispy import app
from vispy import scene

canvas = scene.SceneCanvas(size=(800, 600), show=True, close_keys='escape')

N = 1000
pos = np.empty((N, 2), np.float32)
pos[:, 0] = np.linspace(0., 800., N)
#
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

lines = []




for i in range(20):
    pos = pos.copy()
    pos[:, 1] = np.random.normal(scale=5, loc=i*30, size=N)
    line = scene.visuals.Line(canvas.scene, pos=pos, color=color)
    lines.append(line)
    line.transform = scene.transforms.STTransform()

def update(event):
    for line in lines:
        scale = [np.sin(event.elapsed)+2, np.cos(event.elapsed)+2]
        #line.transform = scene.transforms.STTransform(scale=scale)
        line.transform.scale = scale

timer = app.Timer(interval=0.016, connect=update, start=True)

app.run()
