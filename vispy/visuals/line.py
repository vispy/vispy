# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import print_function, division, absolute_import

import numpy as np

from vispy import gloo
from . import BaseVisual
from ..shaders.composite import ShaderFunction
from .transforms import NullTransform

vertex_shader = """
// local_position function must return the current vertex position
// in the Visual's local coordinate system.
vec4 local_position(void);  

// mapping function that transforms from the Visual's local coordinate
// system to normalized device coordinates.
vec4 map_local_to_nd(vec4);

void main(void) {
    vec4 local_pos = local_position();
    vec4 nd_pos = map_local_to_nd(local_pos);
    gl_Position = nd_pos;
}
"""

fragment_shader = """
void main(void) {
    gl_FragColor = vec4(1, 1, 1, 1);
}
"""    
      

# generate local coordinate from xy (vec2) attribute and z (float) uniform
XYInputFunc = ShaderFunction("""
vec4 v2_f_to_v4(vec2 xy_pos, float z_pos) {
    return vec4(xy_pos, z_pos, 1.0);
}
""")


# generate local coordinate from xyz (vec3) attribute
XYZInputFunc = ShaderFunction("""
vec4 v3_to_v4(vec3 xyz_pos) {
    return vec4(xyz_pos, 1.0);
}
""")


class LineVisual(object):
    def __init__(self, pos):
        self.pos = pos
        self.program = None
        self.transform = NullTransform()
        
    def build_program(self):
        self.vbo = gloo.VertexBuffer(self.pos)
        variables = {}
        if self.pos.shape[-1] == 2:
            inp_func = XYInputFunc
            variables['input_xy_pos'] = self.vbo
            variables['input_z_pos'] = 0.0
            partial = inp_func.bind('local_position', attributes={'xy_pos': 'input_xy_pos'}, uniforms={'z_pos': 'input_z_pos'})
        else:
            inp_func = XYZInputFunc
            variables['input_xyz_pos'] = self.vbo
            partial = inp_func.bind('local_position', attributes={'xyz_pos': 'input_xyz_pos'})
            
        # get function source code for transform
        transform_code = self.transform.GLSL_map
        if not isinstance(transform_code, basestring):
            transform_code = transform_code.code
            
        # get attribute bindings with the name we need
        tr_partial, tr_vars = self.transform.bind_map('map_local_to_nd')
        
        # set program variables required by transform
        variables.update(tr_vars)
        
        vshader = "\n\n".join([vertex_shader, 
                               inp_func.code, partial,
                               transform_code, tr_partial,])

        self.program = gloo.Program(vshader, fragment_shader)
        for k,v in variables.items():
            self.program[k] = v
        
        
    def draw(self):
        if self.program is None:
            self.build_program()
            
        self.program.draw('LINE_STRIP')














#XYPositionFunc = ShaderFunction("""
    #// XY position vertex shader
    #attribute vec2 in_position;
    #uniform float in_z_position;
    
    #vec4 global_position() {
        #return vec4(in_position, in_z_position, 1);            
    #}
#""")

#XYZPositionVertexShader = VertexShader("""
    #// XYZ position vertex shader
    #attribute vec3 in_position;
    
    #vec4 global_position() {
        #return vec4(in_position, 1);            
    #}
#""")

#UniformColorVertexShader = VertexShader("""
    #// Uniform color vertex shader
    #uniform vec4 in_color;
    
    #vec4 global_vertex_color(vec4 pos) {
        #return in_color;
    #}
#""")

#RGBColorVertexShader = VertexShader("""
    #// RGB color vertex shader
    #attribute vec3 in_color;
    #uniform float in_alpha;
    
    #vec4 global_vertex_color(vec4 pos) {
        #return vec4(in_color, in_alpha);            
    #}
#""")

#RGBAColorVertexShader = VertexShader("""
    #// RGBA color vertex shader
    #attribute vec4 in_color;
    
    #vec4 global_vertex_color(vec4 pos) {
        #return vec4(in_color);
    #}
#""")

#NullColorFragmentShader = FragmentShader("""
    #// Null color fragment shader
    #vec4 global_fragment_color(vec4 vert_color, vec4 position) {
        #return vert_color;
    #}
#""")

#vertex_shader = """
#// LineVisual main vertex shader

#// Generic, pluggable shader architecture
#// * declares global callbacks that may be redefined by linking different shaders together
#// * avoids use of potentially expensive conditionals inside the program

##version 120

#// returns current vertex position as vec4
#vec4 global_position();

#// prototype for the transformation to be customized
#vec4 global_transform(vec4);

#vec4 global_vertex_color(vec4);


#varying vec4 vert_color;
#varying vec4 position;
#varying vec4 raw_position;

#void main(void) 
#{
    #// All vertex shaders should implement this line to allow
    #// customizable transformation.
    #raw_position = global_position();
    #position = global_transform(raw_position);
    #gl_Position = position;
    #vert_color = global_vertex_color(position);
#}
#"""

#fragment_shader = """
#// LineVisual main fragment shader
##version 120

#// Returns fragment color given vertex color and position
#// todo: might want access to view, document, and device coordinates here.
#vec4 global_fragment_color(vec4, vec4);

#varying vec4 vert_color;
#varying vec4 position;
#varying vec4 raw_position;

#void main(void)
#{
    #gl_FragColor = global_fragment_color(vert_color, position);
#}
#"""


#class LineProgram(Program):
    #def __init__(self, vfuncs, ffuncs):
        #self.vfuncs = vfuncs
        #self.ffuncs = ffuncs
        
        ## generate all code before proceeding
        #vshader = ""
        #for fn in self.vfuncs:
            #if isinstance(fn, basestring):
                #vshader += fn
            #else:
                #vshader += fn.code()
        #fshader = ""
        #for fn in self.ffuncs:
            #if isinstance(fn, basestring):
                #fshader += fn
            #else:
                #fshader += fn.code()
            
        
        #super(Program, self).__init__(vshader, fshader)


#class LineVisual(BaseVisual):
    #def __init__(self, **kwds):
        ## GL state variables. 
        ## This gives us a suitable set of default values
        ## while allowing the user to override them.        
        #self._gl_options = {
            #gl.GL_LINE_SMOOTH: True,
            #gl.GL_BLEND: True,
            #'glBlendFunc': (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA),
            #'glHint': (gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST),
            #'glLineWidth': (1,),
            #}
            
        #self._opts = {
            #'color': (1, 1, 1, 1),
            #'width': 1,
            #'mode': 'fast',   # maybe 'fast_update', 'fast_redraw', and 'quality' ?
            #}
        #self._program = None
        #self.set_data(**kwds)
        
    #def update(self):
        #self._program = None
        
    #def set_data(self, **kwds):
        #"""
        #Keyword arguments:
        #pos     (N, 2-3) array
        #color   (3-4,) or (N, 3-4) array
        #width   scalar or (N,) array
        #"""
        #self._opts.update(kwds)
        #typ = [('pos', np.float32, self._opts['pos'].shape[-1])]
        #if isinstance(self._opts['color'], np.ndarray):
            #typ.append(('color', np.float32, self._opts['color'].shape[-1]))
        #self._data = np.empty(self._opts['pos'].shape[:-1], typ)
        #self._data['pos'] = self._opts['pos']
        #if isinstance(self._opts['color'], np.ndarray):
            #self._data['color'] = self._opts['color']
        
        #self.vbo = VertexBuffer(self._data)

    #def _generate_program(self):
        #if self._opts['pos'].shape[-1] == 2:
            #posShader = XYPositionVertexShader
        #else:
            #posShader = XYZPositionVertexShader
        
        #if isinstance(self._opts['color'], tuple):
            #colorShader = UniformColorVertexShader
        #elif self._opts['color'].shape[-1] == 3:
            #colorShader = RGBColorVertexShader
        #else:
            #colorShader = RGBAColorVertexShader
            
        #self._program = LineProgram(
            #[
                #vertex_shader, 
                ##self._Visual__transform,
                #self.transform_chain(),
            #], 
            #[
                #fragment_shader,
                #posShader,
                #colorShader,
                #NullColorFragmentShader,
            #])
        
            
        
    #def draw(self):
        ## set up GL state variables
        #for k,v in self._gl_options.items():
            #if v is None:
                #continue
            #if isinstance(k, basestring):
                #func = getattr(gl, k)
                #func(*v)
            #else:
                #if v is True:
                    #gl.glEnable(k)
                #else:
                    #gl.glDisable(k)
        
        #if self._program is None:
            #self._generate_program()
        
        #self._program.attributes['in_position'] = self.vbo['pos']
        #if self._opts['pos'].shape[-1] == 2:
            #self._program.uniforms['in_z_position'] = 1.0

        #if isinstance(self._opts['color'], tuple):
            #self._program.uniforms['in_color'] = self._opts['color']
        #elif self._opts['color'].shape[-1] == 3:
            #self._program.uniforms['in_alpha'] = 1.0;
            #self._program.attributes['in_color'] = self.vbo['color']
        #else:
            #self._program.attributes['in_color'] = self.vbo['color']
                
        #self._program.draw(gl.GL_LINE_STRIP)
        
        

