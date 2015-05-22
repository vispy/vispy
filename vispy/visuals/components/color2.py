# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import weakref

from ..shaders import Function

# To replace color.py soon..


class Alpha(object):
    def __init__(self, alpha=1.0):
        self.shader = Function("""
            void apply_alpha() {
                gl_FragColor.a = gl_FragColor.a * $alpha;
            }
        """)
        self.alpha = alpha
    
    @property
    def alpha(self):
        return self._alpha
    
    @alpha.setter
    def alpha(self, a):
        self._alpha = a
        self.shader['alpha'] = a
        
    def _attach(self, visual):
        self._visual = weakref.ref(visual)
        hook = visual._get_hook('frag', 'post')
        hook.add(self.shader())


class ColorFilter(object):
    def __init__(self, filter=(1, 1, 1, 1)):
        self.shader = Function("""
            void apply_color_filter() {
                gl_FragColor = gl_FragColor * $filter;
            }
        """)
        self.filter = filter
    
    @property
    def filter(self):
        return self._filter
    
    @filter.setter
    def filter(self, f):
        self._filter = tuple(f)
        self.shader['filter'] = self._filter
        
    def _attach(self, visual):
        self._visual = visual
        hook = self._visual._get_hook('frag', 'post')
        hook.add(self.shader())
