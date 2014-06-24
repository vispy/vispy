# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division
import numpy as np

from ...scene.entity import Entity
from ...scene.visuals import Image as ImageVisual
from ...scene.visuals import Line as LineVisual

__all__ = ['Image']


class Image(Entity):
    """
    """
    WrapMethods = ['set_data']

    def __init__(self, *args, **kwds):
        parents = kwds.pop('parents', None)
        Entity.__init__(self, parents)
        self._image = ImageVisual(*args, **kwds)

        w, h = self._image._data.shape[:2]
        self._border = LineVisual(
            pos=np.array([[0, 0], [0, h], [w, h], [w, 0], [0, 0]],
                         dtype=np.float32),
            color=(1, 1, 1, 1))

        for method in self.WrapMethods:
            setattr(self, method, getattr(self._image, method))

    def on_draw(self, event):
        self._image.transform = event.viewport_transform
        self._image.draw()

        self._border.transform = event.viewport_transform
        self._border.draw()
