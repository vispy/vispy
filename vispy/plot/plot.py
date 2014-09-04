# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from ..scene import SceneCanvas, visuals

plots = []


def plot(*args, **kwds):
    """ Create a new canvas and plot the given data. 
    
    For arguments, see scene.visuals.LinePlot.
    """
    canvas = SceneCanvas(keys='interactive')
    canvas.view = canvas.central_widget.add_view()
    canvas.line = visuals.LinePlot(*args, **kwds)
    canvas.view.add(canvas.line)
    canvas.view.camera.auto_zoom(canvas.line)
    canvas.show()
    plots.append(canvas)
    return canvas


def image(*args, **kwds):
    """ Create a new canvas and display the given image data.
    
    For arguments, see scene.visuals.Image.
    """
    canvas = SceneCanvas(keys='interactive')
    canvas.view = canvas.central_widget.add_view()
    canvas.image = visuals.Image(*args, **kwds)
    canvas.view.add(canvas.image)
    canvas.show()
    canvas.view.camera.invert_y = False
    canvas.view.camera.auto_zoom(canvas.image)
    plots.append(canvas)
    return canvas
