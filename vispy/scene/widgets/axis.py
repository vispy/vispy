# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import numpy as np

from .widget import Widget
from ...visuals import AxisVisual


class AxisWidget(Widget):
    """Widget containing an axis

    Parameters
    ----------
    orientation : str
        Orientation of the axis, 'left' or 'bottom'.
    axis_mapping : array-like
        Axis mapping maps a arbitrary array-like object of type numpy array of numpy.datetime64 or
        list of datetime dates
        All other types will be converted to strings
        In case of string mapping the array/list will only be applied to integers
        (0, 1, 2, 3, 4, 5, etc) not (0.5, 0.666, 0.75, 1.5, etc.) floats won't be displayed,
        this is not the case if you provide a array of datetime64 or list of datetime dates
    date_format_string : string
        This string allows you to control the format of the time labels i.e. %m/%d/%Y, %H:%M:%S
        axis_mapping is have to be used, if not this does nothing
        lookup datetime.date.strftime
    axis_label_max_width : int
        Max char length a axis label can have before string will be split in multiple
        rows with max axis_label_max_width chars per row
    **kwargs : dict
        Keyword arguments to pass to AxisVisual.
    """

    def __init__(self, orientation='left', axis_mapping=None, date_format_string=None, axis_label_max_width=18,
                 disable_warning=False, **kwargs):
        if 'tick_direction' not in kwargs:
            tickdir = {'left': (-1, 0), 'right': (1, 0), 'bottom': (0, 1),
                       'top': (0, -1)}[orientation]
            kwargs['tick_direction'] = tickdir
        self.axis = AxisVisual(axis_mapping=axis_mapping, date_format_string=date_format_string,
                               axis_label_max_width=axis_label_max_width, disable_warning=disable_warning, **kwargs)
        self.orientation = orientation
        self._linked_view = None
        Widget.__init__(self)
        self.add_subvisual(self.axis)

    def on_resize(self, event):
        """Resize event handler

        Parameters
        ----------
        event : instance of Event
            The event.
        """
        self._update_axis()

    def _update_axis(self):
        self.axis.pos = self._axis_ends()

    def _axis_ends(self):
        r = self.rect
        if self.orientation == 'left':
            return np.array([[r.right, r.top], [r.right, r.bottom]])
        elif self.orientation == 'bottom':
            return np.array([[r.left, r.bottom], [r.right, r.bottom]])
        elif self.orientation == 'right':
            return np.array([[r.left, r.top], [r.left, r.bottom]])
        elif self.orientation == 'top':
            return np.array([[r.left, r.top], [r.right, r.top]])
        else:
            raise RuntimeError(
                'Orientation %s not supported.' % self.orientation)

    def link_view(self, view):
        """Link this axis to a ViewBox

        This makes it so that the axis's domain always matches the
        visible range in the ViewBox.

        Parameters
        ----------
        view : instance of ViewBox
            The ViewBox to link.
        """
        if view is self._linked_view:
            return
        if self._linked_view is not None:
            self._linked_view.scene.transform.changed.disconnect(
                self._view_changed)
        self._linked_view = view
        view.scene.transform.changed.connect(self._view_changed)
        self._view_changed()

    def _view_changed(self, event=None):
        """Linked view transform has changed; update ticks."""
        tr = self.node_transform(self._linked_view.scene)
        p1, p2 = tr.map(self._axis_ends())
        if self.orientation in ('left', 'right'):
            self.axis.domain = (p1[1], p2[1])
        else:
            self.axis.domain = (p1[0], p2[0])
