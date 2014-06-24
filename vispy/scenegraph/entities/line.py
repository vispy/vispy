# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..entity import Entity
from ...visuals import LineVisual

__all__ = ['Line']


class Line(Entity):
    """
    """
    WrapMethods = []

    def __init__(self, *args, **kwds):
        parents = kwds.pop('parents', None)
        Entity.__init__(self, parents)
        self._visual = LineVisual(*args, **kwds)
        for method in self.WrapMethods:
            setattr(self, method, getattr(self._visual, method))

    def on_paint(self, event):
        self._visual.transform = event.viewport_transform
        self._visual.paint()
