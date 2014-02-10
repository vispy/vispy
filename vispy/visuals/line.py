# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import print_function, division, absolute_import

import numpy as np

from .. import gloo
from ..gloo import gl
from . import BaseVisual
from ..shaders.composite import Function, FunctionTemplate, CompositeProgram
from .transforms import NullTransform



vertex_shader = """
// local_position function must return the current vertex position
// in the Visual's local coordinate system.
vec4 local_position(void);

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

void main(void) {
    gl_FragColor = frag_color();
}
"""    
      

# generate local coordinate from xy (vec2) attribute and z (float) uniform
# Note that the Function and FunctionTemplate approaches
# should work equally well.
#XYInputFunc = Function("""
#vec4 v2_f_to_v4(vec2 xy_pos, float z_pos) {
    #return vec4(xy_pos, z_pos, 1.0);
#}
#""")
XYInputFunc = FunctionTemplate("""
vec4 $func_name() {
    return vec4($xy_pos, $z_pos, 1.0);
}
""", var_names=['xy_pos', 'z_pos'])


# generate local coordinate from xyz (vec3) attribute
#XYZInputFunc = Function("""
#vec4 v3_to_v4(vec3 xyz_pos) {
    #return vec4(xyz_pos, 1.0);
#}
#""")
XYZInputFunc = FunctionTemplate("""
vec4 $func_name() {
    return vec4($xyz_pos, 1.0);
}
""", var_names=['xyz_pos'])

# pair of functions used to provide uniform/attribute input to fragment shader
#RGBAInputFunc = Function("""
#vec4 v4_to_v4(vec4 rgba) {
    #return rgba;
#}
#""")
RGBAInputFunc = FunctionTemplate("""
vec4 $func_name() {
    return $rgba;
}
""", var_names=['rgba'])
RGBAVertexInputFunc = FunctionTemplate("""
void $func_name() {
    $output = $input;
}
""", var_names=['input', 'output'])


class LineVisual(BaseVisual):
    def __init__(self, pos=None, color=None, width=None):
        #super(LineVisual, self).__init__()
        
        self._opts = {
            'pos': None,
            'color': (1, 1, 1, 1),
            'width': 1,
            'transform': NullTransform(),
            }
        
        self._program = None
        self._vbo = None
        
        self.set_data(pos=pos, color=color, width=width)

    @property
    def transform(self):
        return self._opts['transform']
    
    @transform.setter
    def transform(self, tr):
        self._opts['transform'] = tr
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
        self._program = None
        
    def build_program(self):
        
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
        
        
        self._program = CompositeProgram(vmain=vertex_shader, fmain=fragment_shader)
        
        # select the correct function to read in vertex data based on position array shape
        if pos.shape[-1] == 2:
            inp_func = XYInputFunc
            bound_fn = inp_func.bind('local_position', 
                                     xy_pos=('attribute', 'vec2', 'input_xy_pos'),
                                     z_pos=('uniform', 'float', 'input_z_pos'))
            bound_fn['input_xy_pos'] = self._vbo['pos']
            bound_fn['input_z_pos'] = 0.0
        else:
            inp_func = XYZInputFunc
            bound_fn = inp_func.bind('local_position', 
                                     xyz_pos=('attribute', 'vec3', 'input_xyz_pos'))
            bound_fn['input_xyz_pos'] = self._vbo
            
        self._program.set_hook('local_position', bound_fn)
        
        
        # get code and variables needed for transformation fucntions
        tr_bound = self.transform.bind_map('map_local_to_nd')
        self._program.set_hook('map_local_to_nd', tr_bound)
        
        
        # get code and variables needed for fragment coloring
        if color_is_array:
            # variable used to carry color input from vertex shader to 
            # fragment shader:
            varying = ('varying', 'vec4', 'input_color_varying')
            
            # fragment shader function that retrives color from varying:
            color_bound = RGBAInputFunc.bind('frag_color', 
                                             rgba=varying)
            color_bound['input_color'] = self._vbo['color']
            self._program.set_hook('frag_color', color_bound)
            
            # vertex shader function that retrives color from attribute:
            color_frag_bound = RGBAVertexInputFunc.bind(
                                   name='frag_color',
                                   input=('attribute', 'vec4', 'input_color'),
                                   output=varying)
            self._program.add_post_hook(color_frag_bound)
                                                        
            
        else:
            color_bound = RGBAInputFunc.bind('frag_color', 
                                             rgba=('uniform', 'vec4', 'input_color'))
            color_bound['input_color'] = np.array(color)
            self._program.set_hook('frag_color', color_bound)
            

        
    def paint(self):
        if self._opts['pos'] is None or len(self._opts['pos']) == 0:
            return
        
        if self._program is None:
            self.build_program()
            
        gl.glLineWidth(self._opts['width'])
        self._program.draw('LINE_STRIP')














#XYPositionFunc = Function("""
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
        
        #self._vbo = VertexBuffer(self._data)

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
        
        #self._program.attributes['in_position'] = self._vbo['pos']
        #if self._opts['pos'].shape[-1] == 2:
            #self._program.uniforms['in_z_position'] = 1.0

        #if isinstance(self._opts['color'], tuple):
            #self._program.uniforms['in_color'] = self._opts['color']
        #elif self._opts['color'].shape[-1] == 3:
            #self._program.uniforms['in_alpha'] = 1.0;
            #self._program.attributes['in_color'] = self._vbo['color']
        #else:
            #self._program.attributes['in_color'] = self._vbo['color']
                
        #self._program.draw(gl.GL_LINE_STRIP)
        
        

