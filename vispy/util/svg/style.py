# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from . color import Color
from . number import Number
from . length import Length

_converters = {
    "fill": Color,
    "fill-opacity": Number,
    "stroke": Color,
    "stroke-opacity": Number,
    "opacity": Number,
    "stroke-width": Length,
    #    "stroke-miterlimit": Number,
    #    "stroke-dasharray":  Lengths,
    #    "stroke-dashoffset": Length,
}


class Style(object):

    def __init__(self):
        self._unset = True
        for key in _converters.keys():
            key_ = key.replace("-", "_")
            self.__setattr__(key_, None)

    def update(self, content):
        if not content:
            return

        self._unset = False
        items = content.strip().split(";")
        attributes = dict([item.strip().split(":") for item in items if item])
        for key, value in attributes.items():
            if key in _converters:
                key_ = key.replace("-", "_")
                self.__setattr__(key_, _converters[key](value))

    @property
    def xml(self):
        return self._xml()

    def _xml(self, prefix=""):
        if self._unset:
            return ""

        s = 'style="'
        for key in _converters.keys():
            key_ = key.replace("-", "_")
            value = self.__getattribute__(key_)
            if value is not None:
                s += '%s:%s ' % (key, value)
        s += '"'
        return s
