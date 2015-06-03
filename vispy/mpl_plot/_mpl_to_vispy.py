# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
import base64
import warnings

try:
    import matplotlib.pyplot as plt
    from ..ext.mplexporter import Exporter, Renderer
except ImportError as exp:
    Exporter = None
    Renderer = object
    has_mplexporter = False
    why_not = str(exp)
else:
    has_mplexporter = True
    why_not = None

from ..ext.six import BytesIO
from ..color import Color
from ..io import read_png

from ..scene.visuals import Line, Markers, Text, Image
from ..scene.widgets import ViewBox
from ..visuals.transforms import STTransform
from ..scene import SceneCanvas, PanZoomCamera
from ..testing import has_matplotlib


def _check_coords(coords, valid):
    if coords not in valid:
        raise RuntimeError('Coords must be %s, not %s' % (valid, coords))


class VispyRenderer(Renderer):
    def __init__(self, *args, **kwargs):
        self._line_count = 0
        self._axs = {}
        Renderer.__init__(self, *args, **kwargs)

    def open_figure(self, fig, props):
        self._dpi = props['dpi']
        size = (props['figwidth'] * self._dpi,
                props['figheight'] * self._dpi)
        self.canvas = SceneCanvas(size=size, show=True, keys='interactive',
                                  bgcolor='lightgray')

        @self.canvas.events.resize.connect
        def on_resize(event):
            self._resize(*event.size)
        self.canvas.events.resize.connect(on_resize)

    def close_figure(self, fig):
        # self.canvas.close()
        pass  # don't do this, it closes when done rendering

    def open_axes(self, ax, props):
        bounds = np.array(props['bounds'])
        bounds[1] = 1. - bounds[1] - bounds[3]
        xlim = props['xlim']
        ylim = props['ylim']
        # for a in props['axes']:
        #    a['position']  # add borders
        vb = ViewBox(parent=self.canvas.scene, border_color='black',
                     bgcolor=props['axesbg'])
        vb.camera = PanZoomCamera()
        vb.camera.set_range(xlim, ylim, margin=0)
        ax_dict = dict(ax=ax, bounds=bounds, vb=vb, lims=xlim+ylim)
        self._axs[ax] = ax_dict
        self._resize(*self.canvas.size)

    def _resize(self, w, h):
        for ax in self._axs.values():
            ax['vb'].pos = (w * ax['bounds'][0], h * ax['bounds'][1])
            ax['vb'].size = (w * ax['bounds'][2], h * ax['bounds'][3])

    def close_axes(self, ax):
        # self._axs.pop(ax)['vb'].parent = []
        pass  # don't do anything, or all plots get closed (!)

    def open_legend(self, legend, props):
        raise NotImplementedError('Legends not supported yet')

    def close_legend(self, legend):
        pass

    def draw_image(self, imdata, extent, coordinates, style, mplobj=None):
        _check_coords(coordinates, 'data')
        imdata = read_png(BytesIO(base64.b64decode(imdata.encode('utf-8'))))
        assert imdata.ndim == 3 and imdata.shape[2] == 4
        imdata[:, :, 3] = (imdata[:, :, 3] *
                           (style['alpha'] if style['alpha'] is not None
                            else 1.)).astype(np.uint8)
        img = Image(imdata)
        vb = self._mpl_ax_to(mplobj)
        img.transform = STTransform.from_mapping([[0, 0], img.size],
                                                 [[extent[0], extent[3]],
                                                  [extent[1], extent[2]]])
        img.parent = vb.scene

    def draw_text(self, text, position, coordinates, style,
                  text_type=None, mplobj=None):
        _check_coords(coordinates, 'data')
        color = Color(style['color'])
        color.alpha = style['alpha']
        color = color.rgba
        text = Text(text, color=color, pos=position,
                    font_size=style['fontsize'], rotation=style['rotation'],
                    anchor_x=style['halign'], anchor_y=style['valign'])
        text.parent = self._mpl_ax_to(mplobj).scene

    def draw_markers(self, data, coordinates, style, label, mplobj=None):
        _check_coords(coordinates, 'data')
        edge_color = Color(style['edgecolor'])
        edge_color.alpha = style['alpha']
        face_color = Color(style['facecolor'])
        face_color.alpha = style['alpha']
        markers = Markers()
        markers.set_data(data, face_color=face_color, edge_color=edge_color,
                         size=style['markersize'], symbol=style['marker'])
        markers.parent = self._mpl_ax_to(mplobj).scene

    def draw_path(self, data, coordinates, pathcodes, style,
                  offset=None, offset_coordinates="data", mplobj=None):
        _check_coords(coordinates, 'data')
        if offset is not None:
            raise NotImplementedError('cannot handle offset')
            _check_coords(offset_coordinates, 'data')
        # TODO --, :, etc.
        color = Color(style['edgecolor'])
        color.alpha = style['alpha']
        line = Line(data, color=color, width=style['edgewidth'],
                    method='gl')  # XXX Looks bad with agg :(
        line.parent = self._mpl_ax_to(mplobj).scene

    def _mpl_ax_to(self, mplobj, output='vb'):
        """Helper to get the parent axes of a given mplobj"""
        for ax in self._axs.values():
            if ax['ax'] is mplobj.axes:
                return ax[output]
        raise RuntimeError('Parent axes could not be found!')

    def _vispy_done(self):
        """Things to do once all objects have been collected"""
        self._resize(*self.canvas.size)

    # def draw_path_collection(...) TODO add this for efficiency

# https://github.com/mpld3/mplexporter/blob/master/
#                    mplexporter/renderers/base.py


def _mpl_to_vispy(fig):
    """Convert a given matplotlib figure to vispy

    This function is experimental and subject to change!
    Requires matplotlib and mplexporter.

    Parameters
    ----------
    fig : instance of matplotlib Figure
        The populated figure to display.

    Returns
    -------
    canvas : instance of Canvas
        The resulting vispy Canvas.
    """
    renderer = VispyRenderer()
    exporter = Exporter(renderer)
    with warnings.catch_warnings(record=True):  # py3k mpl warning
        exporter.run(fig)
    renderer._vispy_done()
    return renderer.canvas


def show(block=False):
    """Show current figures using vispy

    Parameters
    ----------
    block : bool
        If True, blocking mode will be used. If False, then non-blocking
        / interactive mode will be used.

    Returns
    -------
    canvases : list
        List of the vispy canvases that were created.
    """
    if not has_matplotlib():
        raise ImportError('Requires matplotlib version >= 1.2')
    cs = [_mpl_to_vispy(plt.figure(ii)) for ii in plt.get_fignums()]
    if block and len(cs) > 0:
        cs[0].app.run()
    return cs
