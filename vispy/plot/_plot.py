# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np

from ..scene import SceneCanvas, visuals, cameras, widgets


class Fig(SceneCanvas):
    """Create a figure window"""

    def __init__(self, bgcolor='w', size=(800, 600), show=True):
        super(Fig, self).__init__(bgcolor=bgcolor, keys='interactive',
                                  show=show, size=size)
        self._grid = self.central_widget.add_grid()
        self._plot_widgets = []

    @property
    def plot_widgets(self):
        """List of the PlotWidgets"""
        return tuple(self._plot_widgets)

    def __getitem__(self, idxs):
        """Get an axis"""
        if len(idxs) == 1:
            idxs = idxs + (slice(None),)
        elif len(idxs) != 2:
            raise ValueError('Incorrect index: %s' % (idxs,))
        grid = self._grid
        lims = np.empty((2, 2), int)
        for ii, idx in enumerate(idxs):
            if isinstance(idx, int):
                idx = slice(idx, idx + 1, None)
            if not isinstance(idx, slice):
                raise ValueError('indices must be slices or integers, not %s'
                                 % (type(idx),))
            if idx.step is not None and idx.step != 1:
                raise ValueError('step must be one or None, not %s' % idx.step)
            start = 0 if idx.start is None else idx.start
            end = grid.grid_size[ii] if idx.stop is None else idx.stop
            lims[ii] = [start, end]
        layout = grid.layout_array
        existing = layout[lims[0, 0]:lims[0, 1], lims[1, 0]:lims[1, 1]] + 1
        if existing.any():
            existing = set(list(existing.ravel()))
            ii = list(existing)[0] - 1
            if len(existing) != 1 or ((layout == ii).sum() !=
                                      np.prod(np.diff(lims))):
                raise ValueError('Cannot add widget (collision)')
            return self._grid._grid_widgets[ii][-1]
        spans = np.diff(lims)[:, 0]
        pw = grid.add_widget(_PlotWidget(),
                             row=lims[0, 0], col=lims[1, 0],
                             row_span=spans[0], col_span=spans[1])
        pw.camera = cameras.PanZoomCamera()
        self._plot_widgets += [pw]
        return pw


class _PlotWidget(widgets.ViewBox):
    """Class giving access to plotting"""
    def image(self, data):
        image = visuals.Image(data)
        self.add(image)
        self.camera = cameras.PanZoomCamera(aspect=1)
        self.camera.set_range()
        return image

    def volume(self, data, threshold=None, style='mip', cmap='grays'):
        volume = visuals.Volume(data, threshold=threshold, style=style,
                                cmap=cmap)
        self.add(volume)
        self.camera = cameras.TurntableCamera(azimuth=0,
                                              elevation=0)                
        self.camera.set_range(margin=0)
        return volume