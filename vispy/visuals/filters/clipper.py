# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from ..shaders import Function
from ..transforms import NullTransform
from ...geometry import Rect


clip_frag = """
void clip() {
    vec4 pos = $fb_to_clip(gl_FragCoord);
    if( pos.x < $view.x || pos.x > $view.y || 
        pos.y < $view.z || pos.y > $view.w ) {
        discard;
    }
}
"""


class Clipper(object):
    """Clips visual output to a rectangular region.
    """
    def __init__(self, bounds=(0, 0, 1, 1), transform=None):
        self.clip_shader = Function(clip_frag)
        self.clip_expr = self.clip_shader()
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
        self.clip_shader['view'] = (b.left, b.right, b.bottom, b.top)

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
        self.clip_shader['fb_to_clip'] = tr
        
    def _attach(self, visual):
        try:
            hook = visual._get_hook('frag', 'pre')
        except KeyError:
            raise NotImplementedError("Visual %s does not support clipping" %
                                      visual)
        hook.add(self.clip_expr, position=1)

    def _detach(self, visual):
        visual._get_hook('frag', 'pre').remove(self.clip_expr)
