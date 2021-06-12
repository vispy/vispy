# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from ..scene import SceneCanvas
from .plotwidget import PlotWidget


class Fig(SceneCanvas):
    """Create a figure window

    Parameters
    ----------
    bgcolor : instance of Color
        Color to use for the background.
    size : tuple
        Size of the figure window in pixels.
    show : bool
        If True, show the window.
    **kwargs : dict
        Keywoard arguments to pass to `SceneCanvas` base class.

    Notes
    -----
    You can create a Figure, PlotWidget, and diagonal line plot like this::

        >>> from vispy.plot import Fig
        >>> fig = Fig()
        >>> ax = fig[0, 0]  # this creates a PlotWidget
        >>> ax.plot([[0, 1], [1, 0]])

    See the gallery for many other examples.

    See Also
    --------
    PlotWidget : the axis widget for plotting
    SceneCanvas : the super class
    """

    def __init__(self, bgcolor='w', size=(800, 600), show=True,
                 keys='interactive', **kwargs):
        self._plot_widgets = []
        self._grid = None  # initialize before the freeze occurs
        super(Fig, self).__init__(bgcolor=bgcolor, keys=keys,
                                  show=show, size=size, **kwargs)
        self._grid = self.central_widget.add_grid()
        self._grid._default_class = PlotWidget

    @property
    def plot_widgets(self):
        """List of the associated PlotWidget instances"""
        return tuple(self._plot_widgets)

    def __getitem__(self, idxs):
        """Get an axis"""
        pw = self._grid.__getitem__(idxs)
        self._plot_widgets += [pw]
        return pw
