# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Color components are modular shader components used for retrieving or
generating fragment colors.

These components create a function in the fragment shader that accepts no 
arguments and returns a vec4 color.
"""

from __future__ import division

import numpy as np

from ..visual import VisualComponent
from ...shaders.composite import Function
from ... import gloo


class UniformColorComponent(VisualComponent):
    """
    Generates a uniform color for all vertexes.
    """
    
    CODE = """
        vec4 $colorInput() {
            return $rgba;
        }
        """
    
    def __init__(self, color=(1,1,1,1)):
        self.shader_func = Function(self.CODE)
        self._color = color
        
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, c):
        self._color = c
        
    def _attach(self, visual):
        super(UniformColorComponent, self)._attach(visual)
        visual._program.add_callback('frag_color', self.shader_func)
        
    def _detach(self):
        self.visual._program.remove_callback('frag_color', self.shader_func)
        super(UniformColorComponent, self)._detach()
        
    def activate(self, program, mode):
        self.shader_func['rgba'] = ('uniform', 'vec4', np.array(self._color))

    @property
    def supported_draw_modes(self):
        return (self.DRAW_PRE_INDEXED, self.DRAW_UNINDEXED)


class VertexColorComponent(VisualComponent):
    """
    Reads color in from (N,4) array or vertex buffer.
    """
    
    FRAG_CODE = """
        vec4 $colorInput() {
            return $rgba;
        }
        """
    
    VERT_CODE = """
        void $colorInputSupport() {
            $output_color = $input_color;
        }
        """
    
    def __init__(self, color=None):
        self.frag_func = Function(self.FRAG_CODE)
        self.vert_func = Function(self.VERT_CODE)
        self._color = color
        self._vbo = None
        
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, c):
        self._color = c
        
    @property
    def vbo(self):
        if self._vbo is None:
            self._vbo = gloo.VertexBuffer(self._color)
        return self._vbo
        
    def _attach(self, visual):
        super(VertexColorComponent, self)._attach(visual)
        visual._program.add_callback('frag_color', self.frag_func)
        visual._program.add_callback('vert_post_hook', self.vert_func)
        
    def _detach(self):
        self.visual._program.remove_callback('frag_color', self.frag_func)
        self.visual._program.remove_callback('vert_post_hook', self.vert_func)
        super(VertexColorComponent, self)._detach()
        
    def activate(self, program, mode):
        # explicitly declare a new variable (to be shared)
        # TODO: does this need to be explicit?
        self.frag_func['rgba'] = ('varying', 'vec4')   
        self.vert_func['input_color'] = ('attribute', 'vec4', self.vbo)
        
        # automatically assign same variable to both
        self.vert_func['output_color'] = self.frag_func['rgba']

    @property
    def supported_draw_modes(self):
        return (self.DRAW_PRE_INDEXED, self.DRAW_UNINDEXED)

