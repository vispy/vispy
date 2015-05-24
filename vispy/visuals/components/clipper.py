# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import weakref
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
        self.set_transform(transform)
    
    @property
    def bounds(self):
        return self._bounds
    
    @bounds.setter
    def bounds(self, b):
        self._bounds = Rect(b).normalized()
        b = self._bounds
        self.clip_shader['view'] = (b.left, b.right, b.bottom, b.top)
        
    def _attach(self, visual):
        self._visual = weakref.ref(visual)
        try:
            hook = visual._get_hook('frag', 'pre')
        except KeyError:
            raise NotImplementedError("Visual %s does not support clipping" %
                                      visual)
        hook.add(self.clip_expr)

    def set_transform(self, tr):
        self.clip_shader['fb_to_clip'] = tr
