# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .. import gloo
from ..gloo import gl
from . import Visual, VisualComponent
from ..shaders.composite import (Function, ModularProgram, 
                                 FragmentFunction, FunctionChain)
from .transforms import NullTransform, STTransform



vertex_shader = """
// local_position function must return the current vertex position
// in the Visual's local coordinate system.
//vec4 local_position();

attribute vec2 local_pos;

// mapping function that transforms from the Visual's local coordinate
// system to normalized device coordinates.
vec4 map_local_to_nd(vec4);

// generic hook for executing code after the vertex position has been set
void vert_post_hook();

varying vec2 image_pos;

void main(void) {
    vec4 nd_pos = map_local_to_nd(vec4(local_pos, 0, 1));
    gl_Position = nd_pos;
    image_pos = local_pos;
    vert_post_hook();
}
"""

fragment_shader = """
// maps from local coordinates of the Visual to texture coordinates.
vec4 map_local_to_tex(vec4);

// Generic hook for executing code after the fragment color has been set
// Functions in this hook may modify glFragColor or discard.
void frag_post_hook();

uniform sampler2D tex;
varying vec2 image_pos;

void main(void) {
    vec4 tex_coord = map_local_to_tex(vec4(image_pos,0,1));
    if(tex_coord.x < 0 || tex_coord.x > 1 || 
       tex_coord.y < 0 || tex_coord.y > 1) {
        discard;
    }
    gl_FragColor = texture2D(tex, tex_coord.xy);
    
    frag_post_hook();
}
"""



    
class ImageVisual(Visual):
    """
    Visual subclass displaying an image. 
    
    Parameters:
        data : (height, width, 4) ubyte array
        method : str
            Selects method of rendering image in case of non-linear transforms.
            Each method produces similar results, but may trade efficiency 
            and accuracy. If the transform is linear, this parameter is ignored
            and a single quad is drawn around the area of the image.
            'subdivide': Image is represented as a grid of triangles with
                texture coordinates linearly mapped.
            'impostor': Image is represented as a quad covering the entire
                view, with texture coordinates determined by the transform. This
                produces the best transformation results, but may be slow.
        grid: (rows, cols)
            If method='subdivide', this tuple determines the number of rows and
            columns in the image grid.
    """
    
    def __init__(self, data, method='subdivide', grid=(10,10)):
        super(ImageVisual, self).__init__()
        self.set_gl_options('opaque')
        
        self._data = None
        
        # maps from quad vertexes to ND coordinates
        self._transform = NullTransform()
        
        # maps from quad coordinates to texture coordinates
        self._tex_transform = STTransform() 
        
        self._program = None
        self._texture = None
        #self.pos_input_component = LinePosInputComponent(self)
        #self.color_input_component = LineColorInputComponent(self)
        self._vbo = None
        self._fragment_callbacks = []
        self.set_data(data)
        self.set_gl_options(glCullFace=('GL_FRONT_AND_BACK',))
        
        self.method = method
        self.grid = grid
        

    @property
    def transform(self):
        return self._transform
    
    @transform.setter
    def transform(self, tr):
        self._transform = tr
        self._program = None

    def add_fragment_callback(self, func):
        self._fragment_callbacks.append(func)
        self._program = None

    def set_data(self, data):
        self._data = data
        
        # might need to rebuild vbo or program.. 
        # this could be made more clever.
        self._vbo = None
        self._texture = None
        self._program = None

    def _build_data(self):
        # Construct complete data array with position and optionally color
        if self.transform.Linear:
            method = 'subdivide'
            grid = (1, 1)
        else:
            method = self.method
            grid = self.grid
        
        if self.method == 'subdivide':
            # quads cover area of image as closely as possible
            w = self._data.shape[0] / grid[1]
            h = self._data.shape[1] / grid[0]
            
            quad = np.array([[0,0], [w,h], [w,0], [0,0], [0,h], [w,h]], 
                            dtype=np.float32)
            quads = np.empty((grid[1], grid[0], 6, 2), dtype=np.float32)
            quads[:] = quad
            
            mgrid = np.mgrid[0.:grid[1], 0.:grid[0]].transpose(1,2,0)[:, :, np.newaxis, :]
            mgrid[...,0] *= w
            mgrid[...,1] *= h
            
            quads += mgrid
            self._vbo = gloo.VertexBuffer(quads.reshape(grid[1]*grid[0]*6,2))
        
        elif self.method == 'impostor':
            # quad covers entire view; frag. shader will deal with image shape
            quad = np.array([[-1,-1], [1,1], [1,-1], [-1,-1], [-1,1], [1,1]], 
                            dtype=np.float32)
            self._vbo = gloo.VertexBuffer(quad)
        else:
            raise NotImplementedError
            
        
        self._texture = gloo.Texture2D(self._data)
        self._texture.set_filter('NEAREST', 'NEAREST')
        
        
    def _build_program(self):
        if self._vbo is None:
            self._build_data()
        
        # Create composite program
        program = ModularProgram(vertex_shader, fragment_shader)
        program['local_pos'] = self._vbo
        program['tex'] = self._texture
        #program['image_size'] = self._data.shape[:2]
        
        program.add_chain('vert_post_hook')
        program.add_chain('frag_post_hook')
        
        # Activate position input component
        #self.pos_input_component._activate(program)

        self._tex_transform.scale = (1./self._data.shape[0], 1./self._data.shape[1])
        if self.method == 'subdivide':
            # Attach transformation functions
            program['map_local_to_nd'] = self.transform.shader_map()

            program['map_local_to_tex'] = self._tex_transform.shader_map()
        elif self.method == 'impostor':
            program['map_local_to_nd'] = NullTransform().shader_map()
            program['map_local_to_tex'] = (self._tex_transform * self.transform.inverse()).shader_map()
            
        else:
            raise NotImplementedError
        
        # Activate color input function
        #self.color_input_component._activate(program)
        
        # Attach fragment shader post-hook chain
        for func in self._fragment_callbacks:
            program.add_callback('frag_post_hook', func)
        
        self._program = program
        
        
    def paint(self):
        super(ImageVisual, self).paint()
        
        if self._data is None:
            return
        
        if self._program is None:
            self._build_program()
            
        self._program.draw('TRIANGLES')

