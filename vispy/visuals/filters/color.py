# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import weakref

from ..shaders import Function, Varying
from ...color import colormap


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
        hook = visual._get_hook('frag', 'post')
        hook.add(self.shader(), position=8)


class ZColormapFilter(object):
    def __init__(self, cmap, zrange=(0, 1)):
        self.vshader = Function("""
            void z_colormap_support() {
                $zval = $position.z;
            }
        """)
        self.fshader = Function("""
            void apply_z_colormap() {
                gl_FragColor = $cmap(($zval - $zrange.x) / 
                                     ($zrange.y - $zrange.x));
            }
        """)
        if isinstance(cmap, str):
            cmap = colormap.get_colormap(cmap)
        self.cmap = Function(cmap.glsl_map)
        self.fshader['cmap'] = self.cmap
        self.fshader['zrange'] = zrange
        self.vshader['zval'] = Varying('v_zval', dtype='float')
        self.fshader['zval'] = self.vshader['zval']
        
    def _attach(self, visual):
        self._visual = visual
        vhook = visual._get_hook('vert', 'post')
        vhook.add(self.vshader(), position=9)
        fhook = visual._get_hook('frag', 'post')
        fhook.add(self.fshader(), position=3)
        
        self.vshader['position'] = visual.shared_program.vert['position']
