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
        
    def on_resize(self, event):
        self._update_axis()
        
    def _update_axis(self):
        r = self.inner_rect
        self.axis.pos = np.array([[r.right-20, r.bottom], [r.right-20, r.top]])
        