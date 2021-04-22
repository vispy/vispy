# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from .base_filter import Filter
from ..transforms import NullTransform
from ...geometry import Rect


class Clipper(Filter):
    """Clips visual output to a rectangular region."""

    FRAG_SHADER = """
        void clip() {
            vec4 pos = $fb_to_clip(gl_FragCoord);
            if( pos.x < $view.x || pos.x > $view.y ||
                pos.y < $view.z || pos.y > $view.w ) {
                discard;
            }
        }
    """

    def __init__(self, bounds=(0, 0, 1, 1), transform=None):
        super(Clipper, self).__init__(fcode=self.FRAG_SHADER,
                                      fhook='pre', fpos=1)

        self.bounds = bounds  # (x, y, w, h)
        if transform is None:
            transform = NullTransform()
        self._transform = None
        self.transform = transform

    @property
    def bounds(self):
        """The clipping boundaries.

        This must be a tuple (x, y, w, h) in a clipping coordinate system
        that is defined by the `transform` property.
        """
        return self._bounds

    @bounds.setter
    def bounds(self, b):
        self._bounds = Rect(b).normalized()
        b = self._bounds
        self.fshader['view'] = (b.left, b.right, b.bottom, b.top)

    @property
    def transform(self):
        """The transform that maps from framebuffer coordinates to clipping
        coordinates.
        """
        return self._transform

    @transform.setter
    def transform(self, tr):
        if tr is self._transform:
            return
        self._transform = tr
        self.fshader['fb_to_clip'] = tr
