# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------
from . element import Element
from . transform import Transform


class Transformable(Element):

    """ Transformable SVG element """

    def __init__(self, content=None, parent=None):
        Element.__init__(self, content, parent)

        if isinstance(content, str):
            self._transform = Transform()
            self._computed_transform = self._transform
        else:
            self._transform = Transform(content.get("transform", None))
            self._computed_transform = self._transform
            if parent:
                self._computed_transform = self._transform + \
                    self.parent.transform

    @property
    def transform(self):
        return self._computed_transform
