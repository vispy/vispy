# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Normal components are modular shader components used for retrieving or
generating surface normal vectors.

These components generate a function in the fragment shader that accepts no
arguments and returns a vec4 normal vector. Typically, the normal vector
is computed in the vertex shader and passed by varying to the fragment 
shader.
"""

from __future__ import division

import numpy as np

from ..visual import VisualComponent
from ...shaders.composite import Function
from ... import gloo

class VertexNormalComponent(VisualComponent):
    FRAG_CODE = """
        vec4 $normal() {
            return $norm;
        }
        """
    
    VERT_CODE = """
        void $normal_support() {
            vec3 o = vec3(0,0,0);
            vec3 i = o + $input_normal.xyz;
            $output_normal = map_local_to_nd(vec4(i,1)) - map_local_to_nd(vec4(o,1));
        }
        """
    
    def __init__(self, meshdata, smooth=True):
        self.frag_func = Function(self.FRAG_CODE)
        self.vert_func = Function(self.VERT_CODE)
        self._meshdata = meshdata
        self.smooth = smooth
        self._vbo = None
        self._vbo_mode = None
        
    def _make_vbo(self, mode):
        if self._vbo is None or self._vbo_mode != mode:
            if mode is self.DRAW_PRE_INDEXED:
                index = 'faces'
            else:
                index = None
            if self.smooth:
                norm = self._meshdata.vertexNormals(indexed=index)
            else:
                if index != 'faces':
                    raise Exception("Not possible to draw faceted mesh without"
                                    "pre-indexing.")
                norm = self._meshdata.faceNormals(indexed=index)
            self._vbo = gloo.VertexBuffer(norm)
            self._vbo_mode = mode
        return self._vbo
        
    def _attach(self, visual):
        super(VertexNormalComponent, self)._attach(visual)
        visual._program.add_callback('vert_post_hook', self.vert_func)
        # don't attach the fragment function now; other components 
        # will call it.
        
    def _detach(self):
        self.visual._program.remove_callback('vert_post_hook', self.vert_func)
        super(VertexNormalComponent, self)._detach()
        
    def normal_shader(self):
        """
        Return the fragment shader function that returns a normal vector.        
        """
        return self.frag_func
        
    def activate(self, program, mode):
        # explicitly declare a new variable (to be shared)
        # TODO: does this need to be explicit?
        self.frag_func['norm'] = ('varying', 'vec4')   
        self.vert_func['input_normal'] = ('attribute', 'vec4', 
                                          self._make_vbo(mode))
        
        # automatically assign same variable to both
        self.vert_func['output_normal'] = self.frag_func['norm']

    @property
    def supported_draw_modes(self):
        if self.smooth:
            return (self.DRAW_PRE_INDEXED, self.DRAW_UNINDEXED)
        else:
            # not possible to draw faceted mesh without pre-indexing.
            return (self.DRAW_PRE_INDEXED,)

