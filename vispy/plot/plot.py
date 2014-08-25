# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from ..scene import SceneCanvas, visuals

plots = []


class PlotCanvas(SceneCanvas):
    def __init__(self, keys='interactive', *args, **kwds):
        SceneCanvas.__init__(self, *args, **kwds)
        self.view = self.central_widget.add_view()


def plot(*args, **kwds):
    canvas = PlotCanvas()
    line = visuals.LineMarkers(*args, **kwds)
    canvas.view.add(line)
    canvas.show()
    plots.append(canvas)


def image(*args, **kwds):
    canvas = PlotCanvas()
    image = visuals.Image(*args, **kwds)
    canvas.view.add(image)
    canvas.show()
    plots.append(canvas)
