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

from __future__ import division

import numpy as np

from .. import gloo
from ..gloo import gl
from . import Visual, VisualComponent
from ..shaders.composite import (Function, ModularProgram, FunctionChain)
from .transforms import NullTransform



vertex_shader = """
// local_position function must return the current vertex position
// in the Visual's local coordinate system.
vec4 local_position();

// mapping function that transforms from the Visual's local coordinate
// system to normalized device coordinates.
vec4 map_local_to_nd(vec4);

// generic hook for executing code after the vertex position has been set
void vert_post_hook();

void main(void) {
    vec4 local_pos = local_position();
    vec4 nd_pos = map_local_to_nd(local_pos);
    gl_Position = nd_pos;
    
    vert_post_hook();
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
        self.set_gl_options('translucent')
        
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
        self._fragment_callbacks = []
        self._vertex_callbacks = []
        self.set_data(pos=pos, color=color, width=width)

    @property
    def transform(self):
        return self._opts['transform']
    
    @transform.setter
    def transform(self, tr):
        self._opts['transform'] = tr
        self._program = None

    def add_fragment_callback(self, func):
        self._fragment_callbacks.append(func)
        self._program = None

    def add_vertex_callback(self, func):
        self._vertex_callbacks.append(func)
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
        program = ModularProgram(vertex_shader, fragment_shader)
        
        program.add_chain('vert_post_hook')
        program.add_chain('frag_post_hook')
        
        # Activate position input component
        self.pos_input_component._activate(program)
        
        # Attach transformation function
        program['map_local_to_nd'] = self.transform.shader_map()
        
        # Activate color input function
        self.color_input_component._activate(program)
        
        # Attach fragment shader post-hook chain
        for func in self._fragment_callbacks:
            program.add_callback('frag_post_hook', func)
        for func in self._vertex_callbacks:
            program.add_callback('vert_post_hook', func)
            
        #program['vert_post_hook'] = self._vertex_callbacks
        #program['frag_post_hook'] = self._fragment_callbacks
        
        self._program = program
        
        
    def paint(self):
        super(LineVisual, self).paint()
        
        if self._opts['pos'] is None or len(self._opts['pos']) == 0:
            return
        
        if self._program is None:
            self._build_program()
            
        gl.glLineWidth(self._opts['width'])
        self._program.draw('LINE_STRIP')




class LinePosInputComponent(VisualComponent):
    """
    Input component for LineVisual that selects between two modes of position
    input: 
    
    * vec2 (x,y) attribute and float (z) uniform
    * vec3 (x,y,z) attribute
    
    """
    # generate local coordinate from xy (vec2) attribute and z (float) uniform
    XYInputFunc = Function("""
        vec4 $input_xy_pos() {
            return vec4($xy_pos, $z_pos, 1.0);
        }
        """)

    # generate local coordinate from xyz (vec3) attribute
    XYZInputFunc = Function("""
        vec4 $input_xyz_pos() {
            return vec4($xyz_pos, 1.0);
        }
        """)
    
    def _activate(self, program):
        # select the correct shader function to read in vertex data based on 
        # position array shape
        if self.visual._data['pos'].shape[-1] == 2:
            func = self.XYInputFunc
            func['xy_pos'] = ('attribute', 'vec2', self.visual._vbo['pos'])
            func['z_pos'] = ('uniform', 'float', 0.0)
        else:
            func = self.XYZInputFunc
            func['xyz_pos']=('attribute', 'vec3', self.visual._vbo)
            
        program['local_position'] = func



class LineColorInputComponent(VisualComponent):
    
    #RGBAAttributeFunc = FragmentFunction(
        ## Read color directly from 'rgba' varying
        #"""
            #vec4 $func_name() {
                #return $rgba;
            #}
        #""",
        ## Set varying from vec4 attribute
        #vertex_func=Function("""
            #void $func_name() {
                #$output = $input;
            #}
            #"""),
        ## vertex variable 'output' and fragment variable 'rgba' should both 
        ## be bound to the same vec4 varying.
        #link_vars=[('output', 'rgba')],
        ## where to install vertex_post callback.
        #vert_hook='vert_post_hook'
        #)

    def __init__(self, visual):
        super(LineColorInputComponent, self).__init__(visual)
        self.frag_func = Function("""
            vec4 $colorInput() {
                return $rgba;
            }
            """)
        
        self.support_func = Function("""
            void $colorInputSupport() {
                $output = $input;
            }
            """)
    
    def _activate(self, program):
        # Select uniform- or attribute-input 
        if 'color' in self.visual._data.dtype.fields:
            # explicitly declare a new variable (to be shared)
            # TODO: does this need to be explicit?
            self.frag_func['rgba'] = ('varying', 'vec4')   
            
            program['frag_color'] = self.frag_func
            
            program.add_callback('vert_post_hook', self.support_func)
            self.support_func['input'] = ('attribute', 'vec4', self.visual._vbo['color'])
            self.support_func['output'] = self.frag_func['rgba'] # automatically assign same variable to both
            
        else:
            self.frag_func['rgba'] = ('uniform', 'vec4', np.array(self.visual._opts['color']))
            program['frag_color'] = self.frag_func
            
    