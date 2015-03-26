# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------

from . group import Group
from . viewport import Viewport


class SVG(Group):

    def __init__(self, content=None, parent=None):
        Group.__init__(self, content, parent)
        self._viewport = Viewport(content)

    @property
    def viewport(self):
        return self._viewport

    def __repr__(self):
        s = ""
        for item in self._items:
            s += repr(item) + "\n"
        return s

    @property
    def xml(self):
        return self._xml()

    def _xml(self, prefix=""):
        s = "<svg "
        s += 'id="%s" ' % self._id
        s += self._viewport.xml
        s += self._transform.xml
        s += "\n"
        for item in self._items:
            s += item._xml(prefix=prefix + "    ") + "\n"
        s += "</svg>\n"
        return s
