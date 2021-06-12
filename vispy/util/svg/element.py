# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
import copy
from . style import Style

namespace = '{http://www.w3.org/2000/svg}'


class Element(object):
    """Generic SVG element"""

    def __init__(self, content=None, parent=None):
        self._parent = parent
        self._id = hex(id(self))
        self._style = Style()
        self._computed_style = Style()

        if isinstance(content, str):
            return

        self._id = content.get('id', self._id)
        self._style.update(content.get("style", None))
        self._computed_style = Style()
        if parent and parent.style:
            self._computed_style = copy.copy(parent.style)
            self._computed_style.update(content.get("style", None))

    @property
    def root(self):
        if self._parent:
            return self._parent.root
        return self

    @property
    def parent(self):
        if self._parent:
            return self._parent
        return None

    @property
    def style(self):
        return self._computed_style

    @property
    def viewport(self):
        if self._parent:
            return self._parent.viewport
        return None
