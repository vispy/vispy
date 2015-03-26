# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------


class Number(object):

    def __init__(self, content):
        if not content:
            self._value = 0
        else:
            content = content.strip()
            self._value = float(content)

    def __float__(self):
        return self._value

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return repr(self._value)
