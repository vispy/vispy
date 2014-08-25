# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from ..scene import SceneCanvas, visuals, transforms

__all__ = ['plot', 'image', 'PlotCanvas']

plots = []


class PlotCanvas(SceneCanvas):
    def __init__(self, *args, **kwds):
        SceneCanvas.__init__(self, *args, **kwds)
        self.view = self.central_widget.add_view()


def plot(*args, **kwds):
    canvas = PlotCanvas(keys='interactive')
    line = visuals.PlotLine(*args, **kwds)
    canvas.view.add(line)
    canvas.show()
    plots.append(canvas)


def image(*args, **kwds):
    canvas = SceneCanvas(keys='interactive')
    image = visuals.Image(*args, **kwds)
    canvas.view.add(image)
    canvas.show()
    plots.append(canvas)
