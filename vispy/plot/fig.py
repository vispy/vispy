# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np

from ..scene import SceneCanvas
from .plotwidget import PlotWidget


class Fig(SceneCanvas):
    """Create a figure window"""

    def __init__(self, bgcolor='w', size=(800, 600), show=True):
        super(Fig, self).__init__(bgcolor=bgcolor, keys='interactive',
                                  show=show, size=size)
        self._grid = self.central_widget.add_grid()
        self._grid._default_class = PlotWidget
        self._plot_widgets = []

    @property
    def plot_widgets(self):
        """List of the associated PlotWidget instances"""
        return tuple(self._plot_widgets)

    def __getitem__(self, idxs):
        """Get an axis"""
        pw = self._grid.__getitem__(idxs)
        self._plot_widgets += [pw]
        return pw
