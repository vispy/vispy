# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import re
import math

from . base import units
from .. import logger


class Length(object):

    def __init__(self, content, mode='x', parent=None):

        if not content:
            self._unit = None
            self._value = 0
            self._computed_value = 0
            return

        re_number = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'
        re_unit = r'em|ex|px|in|cm|mm|pt|pc|%'
        re_length = r'(?P<value>%s)\s*(?P<unit>%s)*' % (re_number, re_unit)
        match = re.match(re_length, content)

        if match:
            self._value = float(match.group("value"))
            self._unit = match.group("unit") or "px"
        else:
            self._value = 0.0
            self._unit = None

        scale = 1
        if self._unit == '%':
            if not parent:
                logger.warn("No parent for computing length using percent")
            elif hasattr(parent, 'viewport'):
                w, h = parent.viewport
                if mode == 'x':
                    scale = w
                elif mode == 'y':
                    scale = h
                elif mode == 'xy':
                    scale = math.sqrt(w * w + h * h) / math.sqrt(2.0)
            else:
                logger.warn("Parent doesn't have a viewport")

        self._computed_value = self._value * units[self._unit] * scale

    def __float__(self):
        return self._computed_value

    @property
    def value(self):
        return self._computed_value

    def __repr__(self):
        if self._unit:
            return "%g%s" % (self._value, self._unit)
        else:
            return "%g" % (self._value)


class XLength(Length):

    def __init__(self, content, parent=None):
        Length.__init__(self, content, 'x', parent)


class YLength(Length):

    def __init__(self, content, parent=None):
        Length.__init__(self, content, 'y', parent)


class XYLength(Length):

    def __init__(self, content, parent=None):
        Length.__init__(self, content, 'xy', parent)
