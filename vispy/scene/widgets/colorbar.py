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
    cmap : str | vispy.color.ColorMap
        Either the name of the ColorMap to be used from the standard
        set of names (refer to `vispy.color.get_colormap`),
        or a custom ColorMap object.
        The ColorMap is used to apply a gradient on the colorbar.
    orientation : {'left', 'right', 'top', 'bottom'}
        The orientation of the colorbar, used for rendering. The
        orientation can be thought of as the position of the label
        relative to the color bar.

        When the orientation is 'left' or 'right', the colorbar is
        vertically placed. When it is 'top' or 'bottom', the colorbar is
        horizontally placed. The colorbar automatically resizes when its
        container's dimension changes.

            * 'top': the colorbar is horizontal.
              Color is applied from left to right.
              Minimum corresponds to left and maximum to right.
              Label is to the top of the colorbar

            * 'bottom': Same as top, except that
              label is to the bottom of the colorbar

            * 'left': the colorbar is vertical.
              Color is applied from bottom to top.
              Minimum corresponds to bottom and maximum to top.
              Label is to the left of the colorbar

            * 'right': Same as left, except that the
              label is placed to the right of the colorbar
    label : str
        The label that is to be drawn with the colorbar
        that provides information about the colorbar.
    clim : tuple (min, max)
        the minimum and maximum values of the data that
        is given to the colorbar. This is used to draw the scale
        on the side of the colorbar.
    border_width : float (in px)
        The width of the border the colormap should have. This measurement
        is given in pixels
    border_color : str | vispy.color.Color
        The color of the border of the colormap. This can either be a
        str as the color's name or an actual instace of a vipy.color.Color
    """
    # padding with respect to the major and minor axis
    # units are normalized [0, 1] with 1 representing occupying
    # all of the length along the given axis
    major_axis_padding = 0.1
    minor_axis_padding = 0.8
    # ratio of minor axis to major axis
    minor_axis_ratio = 0.05

    def __init__(self, cmap, orientation,
                 label="", clim=("", ""),
                 border_width=0.0, border_color="black", **kwargs):

        dummy_size = (1, 1)
        self._colorbar = ColorBarVisual(size=dummy_size, cmap=cmap,
                                        orientation=orientation,
                                        label=label, clim=clim,
                                        border_width=border_width,
                                        border_color=border_color, **kwargs)

        Widget.__init__(self)

        self.add_subvisual(self._colorbar)
        self._update_colorbar()

    def on_resize(self, event):
        """Resize event handler

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        self._update_colorbar()

    def _update_colorbar(self):
        self._colorbar.pos = self.rect.center
        self._colorbar.size = \
            ColorBarWidget.calc_size(self.rect, self._colorbar.orientation)

    @staticmethod
    def calc_size(rect, orientation):
        """Calculate a size

        Parameters
        ----------
        rect : rectangle
            The rectangle.
        orientation : str
            Either "bottom" or "top".
        """
        (total_halfx, total_halfy) = rect.center
        if orientation in ["bottom", "top"]:
            (total_major_axis, total_minor_axis) = (total_halfx, total_halfy)
        else:
            (total_major_axis, total_minor_axis) = (total_halfy, total_halfx)

        major_axis = total_major_axis * (1.0 -
                                         ColorBarWidget.major_axis_padding)
        minor_axis = major_axis * ColorBarWidget.minor_axis_ratio

        # if the minor axis is "leaking" from the padding, then clamp
        minor_axis = np.minimum(minor_axis,
                                total_minor_axis *
                                (1.0 - ColorBarWidget.minor_axis_padding))

        return (major_axis, minor_axis)

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
