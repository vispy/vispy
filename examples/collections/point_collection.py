#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: testskip

import numpy as np
from vispy import app, gloo
from vispy.visuals.collections import PointCollection
from panzoom import PanZoom

canvas = app.Canvas(size=(800, 600), show=True, keys='interactive')
gloo.set_viewport(0, 0, canvas.size[0], canvas.size[1])
gloo.set_state("translucent", depth_test=False)

points = PointCollection("agg", color="shared", transform=panzoom.glsl)
points.append(np.random.normal(0.0, 0.5, (10000, 3)), itemsize=5000)
points["color"] = (1, 0, 0, 1), (0, 0, 1, 1)

@canvas.connect
def on_draw(event):
    gloo.clear('white')
    points.draw()


@canvas.connect
def on_resize(event):
    width, height = event.size
    gloo.set_viewport(0, 0, width, height)

panzoom.attach(canvas)
panzoom.add([points])
app.run()
