# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
Simple visual based on GL_LINE_STRIP / GL_LINES


API issues to work out:

    The main vertex and fragment shaders define a few useful hooks, but these
    may need to be rethought in the future as we consider different kinds of 
    modular components. 
    
    Some of the hooks defined here may be applicable to all Visuals (for
    example, map_local_to_nd), but I expect that each Visual may want to define
    a different set of hooks.
    
"""

from __future__ import print_function, division, absolute_import

import numpy as np

from .. import gloo
from ..gloo import gl
from . import Visual, VisualComponent
from ..shaders.composite import (Function, FunctionTemplate, CompositeProgram, 
                                 FragmentFunction, FunctionChain)
from .transforms import NullTransform



vertex_shader = """
// local_position function must return the current vertex position
// in the Visual's local coordinate system.
vec4 local_position();

// mapping function that transforms from the Visual's local coordinate
// system to normalized device coordinates.
vec4 map_local_to_nd(vec4);

// generic hook for executing code after the vertex position has been set
void post_hook();

void main(void) {
    vec4 local_pos = local_position();
    vec4 nd_pos = map_local_to_nd(local_pos);
    gl_Position = nd_pos;
    
    post_hook();
}
"""

fragment_shader = """
// Must return the color for this fragment
// or discard.
vec4 frag_color();

// Generic hook for executing code after the fragment color has been set
// Functions in this hook may modify glFragColor or discard.
void frag_post_hook();

void main(void) {
    gl_FragColor = frag_color();
    
    frag_post_hook();
}
"""    




    
class LineVisual(Visual):
    def __init__(self, pos=None, color=None, width=None):
        super(LineVisual, self).__init__()
        
        self._opts = {
            'pos': None,
            'color': (1, 1, 1, 1),
            'width': 1,
            'transform': NullTransform(),
            }
        
        self._program = None
        self.pos_input_component = LinePosInputComponent(self)
        self.color_input_component = LineColorInputComponent(self)
        self._vbo = None
        self._fragment_hooks = []
        self.set_data(pos=pos, color=color, width=width)

    @property
    def transform(self):
        return self._opts['transform']
    
    @transform.setter
    def transform(self, tr):
        self._opts['transform'] = tr
        self._program = None

    def add_fragment_hook(self, func):
        self._fragment_hooks.append(func)
        self._program = None

    def set_data(self, pos=None, color=None, width=None):
        """
        Keyword arguments:
        pos     (N, 2-3) array
        color   (3-4) or (N, 3-4) array
        width   scalar or (N,) array
        """
        if pos is not None:
            self._opts['pos'] = pos
        if color is not None:
            self._opts['color'] = color
        if width is not None:
            self._opts['width'] = width
            
        # might need to rebuild vbo or program.. 
        # this could be made more clever.
        self._vbo = None
        self._program = None

    def _build_vbo(self):
        # Construct complete data array with position and optionally color
        
        pos = self._opts['pos']
        typ = [('pos', np.float32, pos.shape[-1])]
        color = self._opts['color']
        color_is_array = isinstance(color, np.ndarray) and color.ndim > 1
        if color_is_array:
            typ.append(('color', np.float32, self._opts['color'].shape[-1]))
        
        self._data = np.empty(pos.shape[:-1], typ)
        self._data['pos'] = pos
        if color_is_array:
            self._data['color'] = color
            
        # convert to vertex buffer
        self._vbo = gloo.VertexBuffer(self._data)
        
        
    def _build_program(self):
        if self._vbo is None:
            self._build_vbo()
        
        # Create composite program
        self._program = CompositeProgram(vmain=vertex_shader, fmain=fragment_shader)
        
        # Activate position input component
        self.pos_input_component._activate(self._program)
        
        # Attach transformation function
        tr_bound = self.transform.bind_map('map_local_to_nd')
        self._program.set_hook('map_local_to_nd', tr_bound)
        
        # Activate color input function
        self.color_input_component._activate(self._program)
        
        # Attach fragment shader post-hook chain
        post_chain = self._get_fragment_post_chain()
        self._program.set_hook('frag_post_hook', post_chain)
        
        
    def paint(self):
        super(LineVisual, self).paint()
        
        if self._opts['pos'] is None or len(self._opts['pos']) == 0:
            return
        
        if self._program is None:
            self._build_program()
            
        gl.glLineWidth(self._opts['width'])
        self._program.draw('LINE_STRIP')

    def _get_fragment_post_chain(self):
        return FunctionChain('frag_post_hook', self._fragment_hooks)



class LinePosInputComponent(VisualComponent):
    """
    Input component for LineVisual that selects between two modes of position
    input: 
    
    * vec2 (x,y) attribute and float (z) uniform
    * vec3 (x,y,z) attribute
    
    """
    # generate local coordinate from xy (vec2) attribute and z (float) uniform
    XYInputFunc = FunctionTemplate("""
        vec4 $func_name() {
            return vec4($xy_pos, $z_pos, 1.0);
        }
        """, bindings=['vec2 xy_pos', 'float z_pos'])

    # generate local coordinate from xyz (vec3) attribute
    XYZInputFunc = FunctionTemplate("""
        vec4 $func_name() {
            return vec4($xyz_pos, 1.0);
        }
        """, bindings=['vec3 xyz_pos'])
    
    def activate(self, program):
        # select the correct shader function to read in vertex data based on 
        # position array shape
        if self.visual._data['pos'].shape[-1] == 2:
            func = self.XYInputFunc.bind(
                        name='local_position', 
                        xy_pos=('attribute', 'input_xy_pos'),
                        z_pos=('uniform', 'input_z_pos'))
            func['input_xy_pos'] = self.visual._vbo['pos']
            func['input_z_pos'] = 0.0
        else:
            func = self.XYZInputFunc.bind(
                        name='local_position', 
                        xyz_pos=('attribute', 'input_xyz_pos'))
            func['input_xyz_pos'] = self.visual._vbo
            
        program.set_hook('local_position', func)



class LineColorInputComponent(VisualComponent):
    
    RGBAAttributeFunc = FragmentFunction(
        # Read color directly from 'rgba' varying
        frag_func=FunctionTemplate("""
            vec4 $func_name() {
                return $rgba;
            }
            """, 
            bindings=['vec4 rgba']),
        # Set varying from vec4 attribute
        vertex_post=FunctionTemplate("""
            void $func_name() {
                $output = $input;
            }
            """, 
            bindings=['vec4 input', 'vec4 output']),
        # vertex variable 'output' and fragment variable 'rgba' should both 
        # be bound to the same vec4 varying.
        link_vars=[('output', 'rgba')]
        )


    RGBAUniformFunc = FunctionTemplate("""
    vec4 $func_name() {
        return $rgba;
    }
    """, bindings=['vec4 rgba'])
    
    def activate(self, program):
        # Select uniform- or attribute-input 
        if 'color' in self.visual._data.dtype.fields:
            func = self.RGBAAttributeFunc.bind(
                            name='frag_color',
                            input=('attribute', 'input_color')
                            )
            func['input_color'] = self.visual._vbo['color']
        else:
            func = self.RGBAUniformFunc.bind('frag_color', 
                                             rgba=('uniform', 'input_color'))
            func['input_color'] = np.array(self.visual._opts['color'])
            
        program.set_hook('frag_color', func)
    