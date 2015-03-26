#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: testskip

import numpy as np
from vispy import app, gloo
from vispy.visuals.collections import SegmentCollection


c = app.Canvas(size=(1200, 600), show=True, keys='interactive')
gloo.set_viewport(0, 0, c.size[0], c.size[1])
gloo.set_state("translucent", depth_test=False)

segments = SegmentCollection("agg", linewidth="local")
n = 100
P0 = np.dstack(
    (np.linspace(100, 1100, n), np.ones(n) * 50, np.zeros(n))).reshape(n, 3)
P0 = 2 * (P0 / (1200, 600, 1)) - 1
P1 = np.dstack(
    (np.linspace(110, 1110, n), np.ones(n) * 550, np.zeros(n))).reshape(n, 3)
P1 = 2 * (P1 / (1200, 600, 1)) - 1

segments.append(P0, P1, linewidth=np.linspace(1, 8, n))
segments['antialias'] = 1
segments['viewport'] = 0, 0, 1200, 600


@c.connect
def on_draw(e):
    gloo.clear('white')
    segments.draw()


@c.connect
def on_resize(e):
    width, height = e.size[0], e.size[1]
    gloo.set_viewport(0, 0, width, height)
    segments['viewport'] = 0, 0, width, height

app.run()
