#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: testskip

import numpy as np
from vispy import app, gloo
from vispy.visuals.collections import PathCollection

c = app.Canvas(size=(800, 800), show=True, keys='interactive')
gloo.set_viewport(0, 0, c.size[0], c.size[1])
gloo.set_state("translucent", depth_test=False)


def star(inner=0.5, outer=1.0, n=5):
    R = np.array([inner, outer] * n)
    T = np.linspace(0, 2 * np.pi, 2 * n, endpoint=False)
    P = np.zeros((2 * n, 3))
    P[:, 0] = R * np.cos(T)
    P[:, 1] = R * np.sin(T)
    return P


n = 2500
S = star(n=5)
P = np.tile(S.ravel(), n).reshape(n, len(S), 3)
P *= np.random.uniform(5, 10, n)[:, np.newaxis, np.newaxis]
P[:, :, :2] += np.random.uniform(0, 800, (n, 2))[:, np.newaxis, :]
P = P.reshape(n * len(S), 3)
P = 2 * (P / (800, 800, 1)) - 1

paths = PathCollection(mode="agg")
paths.append(P, closed=True, itemsize=len(S))
paths["linewidth"] = 1.0
paths['viewport'] = 0, 0, 800, 800


@c.connect
def on_draw(e):
    gloo.clear('white')
    paths.draw()


@c.connect
def on_resize(e):
    width, height = e.size[0], e.size[1]
    gloo.set_viewport(0, 0, width, height)
    paths['viewport'] = 0, 0, width, height

app.run()
