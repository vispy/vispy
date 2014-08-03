# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np

try:
    from mplexporter.exporter import Exporter
    from mplexporter.renderers import Renderer
except ImportError as exp:
    Exporter = None
    Renderer = object
    has_mplexporter = False
    why_not = str(exp)
else:
    has_mplexporter = True
    why_not = None

from ..scene.visuals import Text
from ._plotcanvas import PlotCanvas, MarkerVisual, LineVisual
from ..color import Color


class VispyRenderer(Renderer):
    def __init__(self, *args, **kwargs):
        self._line_count = 0
        self._text_count = 0
        Renderer.__init__(self, *args, **kwargs)

    def open_figure(self, fig, props):
        self.canvas = PlotCanvas()

    def close_figure(self, fig):
        pass

    def open_axes(self, ax, props):
        pass

    def close_axes(self, ax):
        pass

    def open_legend(self, legend, props):
        pass

    def close_legend(self, legend):
        pass

    def draw_image(self, imdata, extent, coordinates, style, mplobj=None):
        """
        imdata : string
            base64 encoded png representation of the image
        extent : list
            the axes extent of the image: [xmin, xmax, ymin, ymax]
        coordinates: string
            A string code, which should be either 'data' for data coordinates,
            or 'figure' for figure (pixel) coordinates.
        style : dictionary
            a dictionary specifying the appearance of the image
        """
        raise NotImplementedError

    def draw_text(self, text, position, coordinates, style,
                  text_type=None, mplobj=None):
        raise NotImplementedError
        # TODO We need a context already to render text...
        self._text_count += 1
        label = 'text_%s' % self._text_count
        self.canvas.add_visual(label, Text(text))

    def draw_markers(self, data, coordinates, style, label, mplobj=None):
        pos = data.astype(np.float32)
        n = pos.shape[0]
        # TODO: uniform instead
        color = np.tile(Color(style['facecolor']).rgb, (n, 1))
        # TODO: uniform instead
        size = np.ones(n, np.float32) * style['markersize']
        # TODO: marker style, linewidth, linecolor, etc.
        # TODO: take 'coordinates' into account
        self.canvas.add_visual(label,
                               MarkerVisual(pos=pos, color=color, size=size))

    def draw_path(self, data, coordinates, pathcodes, style,
                  offset=None, offset_coordinates="data", mplobj=None):
        pos = data.astype(np.float32)
        color = Color(style['edgecolor']).rgb
        self.canvas.add_visual('line_%s' % self._line_count,
                               LineVisual(pos=pos, color=color))
        self._line_count += 1

    # def draw_path_collection(...) TODO add this for efficiency

# https://github.com/mpld3/mplexporter/blob/master/mplexporter/renderers/base.py


def show_vispy(fig, run=True):
    """Show matplotlib figure using vispy

    Parameters
    ----------
    fig : instance of matplotlib Figure
        The populated figure to display.
    run : bool
        If True, the canvas application will be run (blocking).

    Returns
    -------
    canvas : instance of Canvas
        The resulting vispy Canvas.
    """
    if not has_mplexporter:
        raise ImportError('Could not import mplexporter (%s)' % why_not)
    renderer = VispyRenderer()
    exporter = Exporter(renderer)
    exporter.run(fig)
    renderer.canvas.show()
    if run:
        renderer.canvas.app.run()
    return renderer.canvas
