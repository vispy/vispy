#! /usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from vispy import app, gloo
from vispy.visuals.collections import PointCollection

# app.use_app('pyqt4')

c = app.Canvas(size=(800, 600), show=True, keys='interactive')
gloo.set_viewport(0, 0, c.size[0], c.size[1])

points = PointCollection("raw", color="shared")
points.append(np.random.normal(0.0,0.5,(10000,3)), itemsize=5000)
points["color"] = (1,0,0,1), (0,0,1,1)

@c.connect
def on_draw(e):
    gloo.clear('white')
    points.draw()

@c.connect
def on_resize(e):
    gloo.set_viewport(0, 0, e.size[0], e.size[1])

app.run()
