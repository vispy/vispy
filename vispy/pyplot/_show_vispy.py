# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
import base64

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

from ..ext.six import BytesIO
from ..color import Color
from ..util.dataio import read_png

from ..scene.visuals import LineVisual, Markers, Text, Image
from ..scene.widgets import ViewBox
from ..scene.transforms import NullTransform, AffineTransform
from ..scene import SceneCanvas


def _check_coords(coords, valid):
    if coords not in valid:
        raise RuntimeError('Coords must be %s, not %s' % (valid, coords))


class VispyRenderer(Renderer):
    def __init__(self, *args, **kwargs):
        self._line_count = 0
        self._text_count = 0
        self._axs = {}
        self._nt = NullTransform()
        Renderer.__init__(self, *args, **kwargs)

    def open_figure(self, fig, props):
        size = (props['figwidth'] * props['dpi'],
                props['figheight'] * props['dpi'])
        self.canvas = SceneCanvas(size=size, show=True, close_keys='escape',
                                  bgcolor='lightgray')

    def close_figure(self, fig):
        pass  # don't close when the mpl figure closes

    def open_axes(self, ax, props):
        bounds = np.array(props['bounds'])
        bounds[1] = 1. - bounds[1] - bounds[3]
        xlim = props['xlim']
        ylim = props['ylim']
        # for a in props['axes']:
        #    a['position']  # add borders
        vb = ViewBox(parent=self.canvas.scene, border=(0, 0, 0, 1),
                     bgcolor=props['axesbg'])
        vb.clip_method = 'fbo'  # necessary for bgcolor
        vb.camera.rect = (xlim[0], ylim[0],
                          xlim[1] - xlim[0], ylim[1] - ylim[0])
        ax_dict = dict(ax=ax, bounds=bounds, vb=vb, lims=xlim+ylim)
        self._axs[ax] = ax_dict
        self._resize(*self.canvas.size)

        # connect it to the proper event
        def on_resize(event):
            self._resize(*event.size)
        self.canvas.events.resize.connect(on_resize)

    def _resize(self, w, h):
        for ax in self._axs.values():
            ax['vb'].pos = (w * ax['bounds'][0], h * ax['bounds'][1])
            ax['vb'].size = (w * ax['bounds'][2], h * ax['bounds'][3])

    def close_axes(self, ax):
        pass  # not needed for now

    def open_legend(self, legend, props):
        raise NotImplementedError('Legends not supported yet')

    def close_legend(self, legend):
        pass

    def draw_image(self, imdata, extent, coordinates, style, mplobj=None):
        _check_coords(coordinates, 'data')
        imdata = read_png(BytesIO(base64.b64decode(imdata.encode('utf-8'))))
        imdata = imdata.astype(np.float32) / 255.
        assert imdata.ndim == 3 and imdata.shape[2] == 4
        imdata[:, :, 3] = style['alpha'] if style['alpha'] is not None else 1.
        image = Image(imdata)
        lims = self._mpl_ax_to(mplobj, 'lims')
        xprop = (extent[1] - extent[0]) / float(lims[1] - lims[0])
        yprop = (extent[3] - extent[2]) / float(lims[3] - lims[2])
        dx = (lims[0] + lims[1]) / 2. - (extent[0] + extent[1]) / 2.
        dy = (lims[2] + lims[3]) / 2. - (extent[2] + extent[3]) / 2.
        xform = AffineTransform()
        xform.scale([xprop, yprop])
        xform.translate([dx, dy])
        # image.transform = xform  # XXX WHERE TO PUT THIS?
        image.parent = self._mpl_ax_to(mplobj).scene

    def draw_text(self, text, position, coordinates, style,
                  text_type=None, mplobj=None):
        _check_coords(coordinates, 'data')
        color = Color(style['color'])
        color.alpha = style['alpha']
        color = color.rgba
        # TODO fix FONTSIZE/aspect ratio
        xform = AffineTransform()
        xform.scale([1, 5])
        xform.rotate(style['rotation'], [0, 0, 1])
        xform.translate((position[0], position[1], 0.))
        text = Text(text, color=color,
                    anchor_x=style['halign'], anchor_y=style['valign'])
        text.transform = xform
        text.parent = self._mpl_ax_to(mplobj).scene

    def draw_markers(self, data, coordinates, style, label, mplobj=None):
        _check_coords(coordinates, 'data')
        edge_color = Color(style['edgecolor'])
        edge_color.alpha = style['alpha']
        face_color = Color(style['facecolor'])
        face_color.alpha = style['alpha']
        markers = Markers()
        markers.set_data(data, face_color=face_color, edge_color=edge_color,
                         size=style['markersize'], style=style['marker'])
        markers.parent = self._mpl_ax_to(mplobj).scene

    def draw_path(self, data, coordinates, pathcodes, style,
                  offset=None, offset_coordinates="data", mplobj=None):
        _check_coords(coordinates, 'data')
        if offset is not None:
            raise NotImplementedError('cannot handle offset')
            _check_coords(offset_coordinates, 'data')
        # TODO linewidth, etc.
        color = Color(style['edgecolor'])
        color.alpha = style['alpha']
        line = LineVisual(data, color=color)
        line.parent = self._mpl_ax_to(mplobj).scene

    def _mpl_ax_to(self, mplobj, output='vb'):
        """Helper to get the parent axes of a given mplobj"""
        for ax in self._axs.values():
            if ax['ax'] is mplobj.axes:
                return ax[output]
        raise RuntimeError('Parent axes could not be found!')

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
    if run:
        renderer.canvas.app.run()
    return renderer.canvas
