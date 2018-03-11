#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: testskip

import numpy as np
from vispy import app, gloo
from vispy.visuals.collections import PathCollection, PolygonCollection


canvas = app.Canvas(size=(800, 800), show=True, keys='interactive')
gloo.set_viewport(0, 0, canvas.size[0], canvas.size[1])
gloo.set_state("translucent", depth_test=False)


def star(inner=0.5, outer=1.0, n=5):
    R = np.array([inner, outer] * n)
    T = np.linspace(0, 2 * np.pi, 2 * n, endpoint=False)
    P = np.zeros((2 * n, 3))
    P[:, 0] = R * np.cos(T)
    P[:, 1] = R * np.sin(T)
    return P

paths = PathCollection("agg", color='shared')
polys = PolygonCollection("raw", color='shared')

P = star()

n = 100
for i in range(n):
    c = i / float(n)
    x, y = np.random.uniform(-1, +1, 2)
    s = 100 / 800.0
    polys.append(P * s + (x, y, i / 1000.), color=(1, 0, 0, .5))
    paths.append(
        P * s + (x, y, (i - 1) / 1000.), closed=True, color=(0, 0, 0, .5))

paths["linewidth"] = 1.0
paths['viewport'] = 0, 0, 800, 800


@canvas.connect
def on_draw(e):
    gloo.clear('white')
    polys.draw()
    paths.draw()


@canvas.connect
def on_resize(event):
    width, height = event.size
    gloo.set_viewport(0, 0, width, height)
    paths['viewport'] = 0, 0, width, height

app.run()
