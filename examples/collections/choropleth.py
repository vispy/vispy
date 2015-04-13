#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: testskip

import json

import numpy as np

from vispy import app, gloo
from vispy.util import load_data_file
from vispy.visuals.collections import PathCollection, PolygonCollection
from vispy.visuals.transforms import PanZoomTransform


path = load_data_file('uscounties/uscounties.geojson')
with open(path, 'r') as f:
    geo = json.load(f)


def unique_rows(data):
    v = data.view(data.dtype.descr * data.shape[1])
    _, idx = np.unique(v, return_index=True)
    return data[np.sort(idx)]


def add(P, color):
    P = np.array(P)
    if len(P) < 2:
        return
    P = np.array(P) / 20.0 + (5, -2)
    p = np.zeros((len(P), 3))
    p[:, :2] = P
    p = unique_rows(p)
    if len(p) > 1:
        paths.append(p, closed=True)
    if len(p) > 2:
        polys.append(p, color=color)


# Create the canvas.
canvas = app.Canvas(size=(800, 800), keys='interactive')
gloo.set_viewport(0, 0, canvas.size[0], canvas.size[1])
gloo.set_state("translucent", depth_test=False)

panzoom = PanZoomTransform(canvas, aspect=1)
paths = PathCollection(mode="agg+", color="global", transform=panzoom)
polys = PolygonCollection("raw", color="local", transform=panzoom)
paths.update.connect(canvas.update)

for feature in geo["features"]:
    if feature["geometry"]["type"] == 'Polygon':
        path = feature["geometry"]["coordinates"]
        rgba = np.random.uniform(0.5, .8, 4)
        rgba[3] = 1
        add(path[0], color=rgba)

    elif feature["geometry"]["type"] == 'MultiPolygon':
        coordinates = feature["geometry"]["coordinates"]
        for path in coordinates:
            rgba = np.random.uniform(0.5, .8, 4)
            rgba[3] = 1
            add(path[0], color=rgba)

paths["color"] = 0, 0, 0, 1
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

if __name__ == '__main__':
    canvas.show()
    app.run()
