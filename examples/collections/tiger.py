#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: testskip
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
# Distributed under the (new) BSD License.
# -----------------------------------------------------------------------------

from vispy import app, gloo
from vispy.util import load_data_file
from vispy.util.svg import Document
from vispy.visuals.collections import PathCollection, PolygonCollection
from vispy.visuals.transforms import PanZoomTransform

path = load_data_file('tiger/tiger.svg')
tiger = Document(path)

width, height = int(tiger.viewport.width), int(tiger.viewport.height)
canvas = app.Canvas(size=(width, height), show=True, keys='interactive')
gloo.set_viewport(0, 0, width, height)
gloo.set_state("translucent", depth_test=True)

panzoom = PanZoomTransform(canvas, aspect=1.0)
paths = PathCollection(
    "agg+", linewidth='shared', color="shared", transform=panzoom)
polys = PolygonCollection("agg", transform=panzoom)
paths.update.connect(canvas.update)

z = 0
for path in tiger.paths:
    for vertices, closed in path.vertices:

        vertices = 2 * (vertices / (width, height, 1)) - 1
        vertices[:, 1] = -vertices[:, 1]
        if len(vertices) < 3:
            continue
        if path.style.stroke is not None:
            vertices[:, 2] = z - 0.5 / 1000.
            if path.style.stroke_width:
                stroke_width = path.style.stroke_width.value
            else:
                stroke_width = 2.0
            paths.append(vertices, closed=closed, color=path.style.stroke.rgba,
                         linewidth=stroke_width)
        if path.style.fill is not None:
            if path.style.stroke is None:
                vertices[:, 2] = z - 0.25 / 1000.
                paths.append(vertices, closed=closed,
                             color=path.style.fill.rgba,
                             linewidth=1)
            vertices[:, 2] = z
            polys.append(vertices, color=path.style.fill.rgba)
    z -= 1 / 1000.


paths["linewidth"] = 1.0
paths['viewport'] = 0, 0, 800, 800


@canvas.connect
def on_draw(e):
    gloo.clear('white')
    polys.draw()
    paths.draw()


@canvas.connect
def on_resize(e):
    width, height = e.size[0], e.size[1]
    gloo.set_viewport(0, 0, width, height)
    paths['viewport'] = 0, 0, width, height

if __name__ == '__main__':
    canvas.show()
    app.run()
