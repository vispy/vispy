# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


"""
Simple visual based on GL_LINE_STRIP / GL_LINES


API issues to work out:

  * Currently this only uses GL_LINE_STRIP. Should add a 'method' argument like
    ImageVisual.method that can be used to select higher-quality triangle 
    methods.
    
  * The main vertex and fragment shaders define a few useful hooks, but these
    may need to be rethought in the future as we consider different kinds of 
    modular components. 
    
  * Some of the hooks defined here may be applicable to all Visuals (for
    example, map_local_to_nd), but I expect that each Visual may want to define
    a different set of hooks.
    
  * 'pos_input_component' and 'color_input_component' are verbose and ugly.
  
  * Add a few different position input components:
        - X values from vertex buffer of index values, Xmin, and Xstep
        - position from float texture
        
    
"""

from __future__ import division

import numpy as np

from .. import gloo
from .visual import Visual
from .components import (XYPosComponent, XYZPosComponent, 
                         UniformColorComponent, VertexColorComponent)


class LineVisual(Visual):
    """
    Displays multiple line segments.
    """
    def __init__(self, pos=None, **kwds):
        super(LineVisual, self).__init__()
        
        glopts = kwds.pop('gl_options', 'translucent')
        self.set_gl_options(glopts)
        
        if kwds:
            self.set_data(pos, **kwds)

    def set_data(self, pos=None, edges=None, z=0.0, color=(1,1,1,1)):
        """
        *pos* must be array of shape (..., 2) or (..., 3).
        *z* is only used in the former case.
        """
        # select input component based on pos.shape
        if pos is not None:
            if pos.shape[-1] == 2:
                if not isinstance(self.pos_component, XYPosComponent):
                    self.pos_component = XYPosComponent()
                self.pos_component.set_data(xy=pos, z=z, index=edges)
            elif pos.shape[-1] == 3:
                if not isinstance(self.pos_component, XYZPosComponent):
                    self.pos_component = XYZPosComponent()
                self.pos_component.set_data(pos=pos, index=edges)
            
        if isinstance(color, tuple):
            self.fragment_components = [UniformColorComponent(color)]
        elif isinstance(color, np.ndarray):
            self.fragment_components = [VertexColorComponent(color)]
            
    @property
    def primitive(self):
        # TODO: add support for GL_LINES, GL_TRIANGLES
        return gloo.gl.GL_LINE_STRIP


#import numpy as np

#from .. import gloo
#from ..gloo import gl
#from .visual import Visual, VisualComponent
#from ..shaders.composite import Function, ModularProgram, FunctionChain
#from .transforms import NullTransform

#class LineVisual(Visual):
    #def __init__(self, pos=None, color=None, width=None):
        #super(LineVisual, self).__init__()
        #self.set_gl_options('translucent')
        
        #self._opts = {
            #'pos': None,
            #'color': (1, 1, 1, 1),
            #'width': 1,
            #'transform': None,
            #}
        
        ##self._program = ModularProgram(vertex_shader, fragment_shader)
        
        ##self.transform = NullTransform()
        
        ### Generic chains for attaching post-processing functions
        ##self._program.add_chain('vert_post_hook')
        ##self._program.add_chain('frag_post_hook')
        
        ### Components for plugging different types of position and color input.
        ##self._pos_input_component = None
        ##self._color_input_component = None
        ##self.pos_input_component = LinePosInputComponent(self)
        ##self.color_input_component = LineColorInputComponent(self)
        
        ##self._vbo = None
        #self.set_data(pos=pos, color=color, width=width)
        
    #@property
    #def primitive(self):
        ## TODO: add GL_LINE_STRIP, GL_TRIANGLES support
        #return gloo.gl.GL_LINES

    ##@property
    ##def transform(self):
        ##return self._opts['transform']
    
    ##@transform.setter
    ##def transform(self, tr):
        ##self._opts['transform'] = tr
        ##self.events.update()

    ##def add_fragment_callback(self, func):
        ##self._program.add_callback('frag_post_hook', func)
        ##self.events.update()

    ##def add_vertex_callback(self, func):
        ##self._program.add_callback('vert_post_hook', func)
        ##self.events.update()

    ##@property
    ##def pos_input_component(self):
        ##return self._pos_input_component

    ##@pos_input_component.setter
    ##def pos_input_component(self, component):
        ##if self._pos_input_component is not None:
            ##self._pos_input_component._detach(self)
            ##self._pos_input_component = None
        ##component._attach(self)
        ##self._pos_input_component = component
        ##self.events.update()
        
    ##@property
    ##def color_input_component(self):
        ##return self._color_input_component

    ##@color_input_component.setter
    ##def color_input_component(self, component):
        ##if self._color_input_component is not None:
            ##self._color_input_component._detach(self)
            ##self._color_input_component = None
        ##component._attach(self)
        ##self._color_input_component = component
        ##self.events.update()
        

    #def set_data(self, pos=None, color=None, width=None):
        #"""
        #Keyword arguments:
        #pos     (N, 2-3) array
        #color   (3-4) or (N, 3-4) array
        #width   scalar or (N,) array
        #"""
        #if pos is not None:
            #self._opts['pos'] = pos
        #if color is not None:
            #self._opts['color'] = color
        #if width is not None:
            #self._opts['width'] = width
            
        ## TODO: this could be made more clever--might be able to simply 
        ## re-upload data to VBO.
        #self._vbo = None
        #self.events.update()

    ##def _build_vbo(self):
        ### Construct complete data array with position and optionally color
        
        ##pos = self._opts['pos']
        ##typ = [('pos', np.float32, pos.shape[-1])]
        ##color = self._opts['color']
        ##color_is_array = isinstance(color, np.ndarray) and color.ndim > 1
        ##if color_is_array:
            ##typ.append(('color', np.float32, self._opts['color'].shape[-1]))
        
        ##self._data = np.empty(pos.shape[:-1], typ)
        ##self._data['pos'] = pos
        ##if color_is_array:
            ##self._data['color'] = color

        ### convert to vertex buffer
        ##self._vbo = gloo.VertexBuffer(self._data)
        
    ##def paint(self):
        ##super(LineVisual, self).paint()
        
        ##if self._opts['pos'] is None or len(self._opts['pos']) == 0:
            ##return
        
        ##if self._vbo is None:
            ##self._build_vbo()
            
            ### tell components to use the new VBO data
            ##self.pos_input_component.update()
            ##self.color_input_component.update()
            
        ### TODO: this must be optimized.
        ##self._program['map_local_to_nd'] = self.transform.shader_map()
            
        ##gl.glLineWidth(self._opts['width'])
        ##self._program.draw(gl.GL_LINE_STRIP)




##class LinePosInputComponent(VisualComponent):
    ##"""
    ##Input component for LineVisual that selects between two modes of position
    ##input: 
    
    ##* vec2 (x,y) attribute and float (z) uniform
    ##* vec3 (x,y,z) attribute
    
    ##"""
    ### generate local coordinate from xy (vec2) attribute and z (float) uniform
    ##XYInputCode = """
        ##vec4 $input_xy_pos() {
            ##return vec4($xy_pos, $z_pos, 1.0);
        ##}
        ##"""

    ### generate local coordinate from xyz (vec3) attribute
    ##XYZInputCode = """
        ##vec4 $input_xyz_pos() {
            ##return vec4($xyz_pos, 1.0);
        ##}
        ##"""
    
    ##def __init__(self, visual=None):
        ##super(LinePosInputComponent, self).__init__(visual)
        ##self.xy_input_func = Function(self.XYInputCode)
        ##self.xyz_input_func = Function(self.XYZInputCode)
    
    ##def update(self):
        ### select the correct shader function to read in vertex data based on 
        ### position array shape
        ##if self.visual._data['pos'].shape[-1] == 2:
            ##func = self.xy_input_func
            ##func['xy_pos'] = ('attribute', 'vec2', self.visual._vbo['pos'])
            ##func['z_pos'] = ('uniform', 'float', 0.0)
        ##else:
            ##func = self.xyz_input_func
            ##func['xyz_pos']=('attribute', 'vec3', self.visual._vbo)
            
        ##self.visual._program['local_position'] = func



##class LineColorInputComponent(VisualComponent):
    
    ###RGBAAttributeFunc = FragmentFunction(
        #### Read color directly from 'rgba' varying
        ###"""
            ###vec4 $func_name() {
                ###return $rgba;
            ###}
        ###""",
        #### Set varying from vec4 attribute
        ###vertex_func=Function("""
            ###void $func_name() {
                ###$output = $input;
            ###}
            ###"""),
        #### vertex variable 'output' and fragment variable 'rgba' should both 
        #### be bound to the same vec4 varying.
        ###link_vars=[('output', 'rgba')],
        #### where to install vertex_post callback.
        ###vert_hook='vert_post_hook'
        ###)

    ##def __init__(self, visual):
        ##super(LineColorInputComponent, self).__init__(visual)
        ##self.frag_func = Function("""
            ##vec4 $colorInput() {
                ##return $rgba;
            ##}
            ##""")
        
        ##self.support_func = Function("""
            ##void $colorInputSupport() {
                ##$output_color = $input_color;
            ##}
            ##""")
    
    ##def update(self):
        ### Select uniform- or attribute-input 
        ##program = self.visual._program
        ##if 'color' in self.visual._data.dtype.fields:
            ### explicitly declare a new variable (to be shared)
            ### TODO: does this need to be explicit?
            ##self.frag_func['rgba'] = ('varying', 'vec4')   
            
            ##program['frag_color'] = self.frag_func
            
            ##program.add_callback('vert_post_hook', self.support_func)
            ##self.support_func['input_color'] = ('attribute', 'vec4', self.visual._vbo['color'])
            ##self.support_func['output_color'] = self.frag_func['rgba'] # automatically assign same variable to both
            
        ##else:
            ##self.frag_func['rgba'] = ('uniform', 'vec4', np.array(self.visual._opts['color']))
            ##program['frag_color'] = self.frag_func
            