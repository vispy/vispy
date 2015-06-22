# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import numpy as np

from .widget import Widget
from ...visuals import AxisVisual


class AxisWidget(Widget):
    def __init__(self, orientation='left', **kwargs):
        self.axis = AxisVisual(**kwargs)
        Widget.__init__(self)
        self.add_subvisual(self.axis)
        self._linked_view = None
        
    def on_resize(self, event):
        self._update_axis()
        
    def _update_axis(self):
        r = self.inner_rect
        self.axis.pos = np.array([[r.right, r.bottom], [r.right, r.top]])
        
    def link_view(self, view):
        """Link this axis to a ViewBox such that its domain always matches the
        visible range in the ViewBox.
        """
        if view is self._linked_view:
            return
        if self._linked_view is not None:
            self._linked_view.scene.transform.changed.disconnect(self._view_changed)
        self._linked_view = view
        view.scene.transform.changed.connect(self._view_changed)
        self._view_changed()
        
    def _view_changed(self, event=None):
        """Linked view transform has changed; update ticks.
        """
        tr = self.node_transform(self._linked_view.scene)
        r = self.inner_rect
        p1 = tr.map((r.right, r.bottom))
        p2 = tr.map((r.right, r.top))
        self.axis.domain = (p1[1], p2[1])
        
        