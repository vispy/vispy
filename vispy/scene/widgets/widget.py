# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..visuals.visual import Visual
from ..transforms import STTransform
from ...util.event import Event
from ...util.geometry import Rect


class Widget(Visual):
    """ A widget takes up a rectangular space, intended for use in
    a 2D pixel coordinate frame.

    The widget is positioned using the transform attribute (as any
    entity), and its extend (size) is kept as a separate property.

    This is a simple preliminary version!
    """

    def __init__(self, *args, **kwargs):
        #Entity.__init__(self, *args, **kwargs)
        Visual.__init__(self, *args, **kwargs)
        self.events.add(rect_change=Event)
        self._size = 16, 16
        self.transform = STTransform()
        # todo: TTransform (translate only for widgets)

    @property
    def pos(self):
        return tuple(self.transform.translate[:2])

    @pos.setter
    def pos(self, p):
        assert isinstance(p, tuple)
        assert len(p) == 2
        self.transform.translate = p[0], p[1], 0, 0
        self.events.rect_change()

    @property
    def size(self):
        # Note that we cannot let the size be reflected in the transform.
        # Consider a widget of 40x40 in a pixel grid, a child widget therin
        # with size 20x20 would get a scale of 800x800!
        return self._size

    @size.setter
    def size(self, s):
        assert isinstance(s, tuple)
        assert len(s) == 2
        self._size = s
        self.events.rect_change()

    @property
    def rect(self):
        return Rect((0, 0), self.size)
