# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import numpy as np

from .widget import Widget
from ...visuals import ColorBarVisual


class ColorBarWidget(Widget):
    """Widget containing a ColorBar

    Parameters
    ----------
    **kwargs : dict
        Keyword arguments to pass to ColorBarVisual.
    """
    def __init__(self, **kwargs):
        colorbar_args = kwargs

        self._colorbar = ColorBarVisual(**colorbar_args)
        Widget.__init__(self)
        self.add_subvisual(self._colorbar)
        self._set_pos()

    def on_resize(self, event):
        """Resize event handler

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        self._set_pos()

    def _set_pos(self):
        # keep the ColorBar at (0, 0, 0), but move the coordinate of the
        # Widget to the center of the rect.
        self._colorbar.pos = self.rect.center

    @property
    def cmap(self):
        return self._colorbar.cmap

    @cmap.setter
    def cmap(self, cmap):
        self._colorbar.cmap = cmap

    @property
    def label(self):
        return self._colorbar.label

    @label.setter
    def label(self, label):
        self._colorbar.label = label

    @property
    def clim(self):
        return self._colorbar.clim

    @clim.setter
    def clim(self, clim):
        self._colorbar.clim = clim

    @property
    def orientation(self):
        return self._colorbar.orientation
