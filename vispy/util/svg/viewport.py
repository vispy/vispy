# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------

from . length import XLength, YLength


class Viewport(object):

    def __init__(self, content=None, parent=None):

        self._x = None
        self._computed_x = 0
        if content.get('x'):
            self._x = XLength(content.get('x'), parent)
            self._computed_x = float(self._x)

        self._y = None
        self._computed_y = 0
        if content.get('y'):
            self._y = XLength(content.get('y'), parent)
            self._computed_y = float(self._y)

        self._width = None
        self._computed_width = 800
        if content.get('width'):
            self._width = XLength(content.get('width'), parent)
            self._computed_width = float(self._width)

        self._height = None
        self._computed_height = 800
        if content.get('height'):
            self._height = YLength(content.get('height'), parent)
            self._computed_height = float(self._height)

    @property
    def x(self):
        return self._computed_x

    @property
    def y(self):
        return self._computed_y

    @property
    def width(self):
        return self._computed_width

    @property
    def height(self):
        return self._computed_height

    def __repr__(self):
        s = repr((self._x, self._y, self._width, self._height))
        return s

    @property
    def xml(self):
        return self._xml

    @property
    def _xml(self, prefix=""):
        s = ""
        if self._x:
            s += 'x="%s" ' % repr(self._x)
        if self._y:
            s += 'y="%s" ' % repr(self._y)
        if self._width:
            s += 'width="%s" ' % repr(self._width)
        if self._height:
            s += 'height="%s" ' % repr(self._height)
        return s
