# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Notes:

  - Should have swappable input component to allow a variety of different 
    vertex inputs:
        2d attribute + z uniform
        3d attribute
        2d attribute + z uniform + index
        3d attribute + index
        1d attribute + x/y ranges (surface plot)
        (and any other custom input component the user might come up with)
        
  - Should have swappable / chainable fragment components:
        Per-vertex normals (for smooth surfaces)
        Per-face normals (for faceted surfaces)
        Colors per-vertex, per-face
        Materials - phong, etc.
        Textures - color, bump map, spec map, etc
        Wireframe rendering (note this might require vertex modification)
        
  - For efficiency, the vertex inputs should allow both pre-index and 
    unindexed arrays. However, many fragment shaders may require pre-indexed
    arrays. For example, drawing faceted surfaces is not possible with 
    unindexed arrays since the normal vector changes each time a vertex is
    visited.
        => this means that input components need a way to convert their data
           and suggest a different input component (?)
        => More generally, we need to be able to map out all of the available
           pathways and choose the most efficient one based on the input
           data format (to avoid unnecessary conversions) and the requirements
           of individual components (including indexed/unindexed, whether
           geometry shaders are available, ...)
    
  - Fragment shaders that do not need normals should obviously not compute them
  
  - Some materials require a normal vector, but there may be any number of
    ways to generate a normal: per-vertex interpolated, per-face, bump maps,
    etc. This means we need a way for one material to indicate that it requires
    normals, and a way to tell the component which normal-generating component
    it should use.
        => Likewise with colors. In fact, normals and colors are similar enough
           that they could probably share most of the same machinery..
           

    => Color chain   \
                      ===>  Material chain
    => Normal chain  /

    Examples:
        Color input / filters:
            uniform color
            color by vertex, color by face
            texture color
            float texture + colormap
            color by height
            grid contours
            wireframe
        
        Normal input:
            normal per vertex
            normal per face
            texture bump map
            texture normal map
        
        Material composition:
            shaded / facets
            shaded / smooth
            phong shading

"""


from __future__ import division

import numpy as np

from .. import gloo
from .visual import Visual, VisualComponent
from .transforms import NullTransform
from ..shaders.composite import ModularProgram
from ..util.meshdata import MeshData
from .components import (XYPosComponent, XYZPosComponent, 
                         UniformColorComponent, VertexColorComponent)


VERTEX_SHADER = """
// local_position function must return the current vertex position
// in the Visual's local coordinate system.
vec4 local_position();

// mapping function that transforms from the Visual's local coordinate
// system to normalized device coordinates.
vec4 map_local_to_nd(vec4);

// generic hook for executing code after the vertex position has been set
void vert_post_hook();

// Global variable storing the results of local_position()
// Any component may read this variable, but it should be treated as
// read-only.
vec4 local_pos;

void main(void) {
    local_pos = local_position();
    vec4 nd_pos = map_local_to_nd(local_pos);
    gl_Position = nd_pos;
    
    vert_post_hook();
}
"""

FRAGMENT_SHADER = """
// Fragment shader consists of only a single hook that is usually defined 
// by a chain of functions, each which sets or modifies the current fragment
// color, or discards it.
vec4 frag_color();

void main(void) {
    gl_FragColor = frag_color();
}
"""



class MeshVisual(Visual):
    """
    Displays a 3D triangle mesh.
    """
    def __init__(self, **kwds):
        super(MeshVisual, self).__init__()
        
        self._program = ModularProgram(VERTEX_SHADER, FRAGMENT_SHADER)
        
        self.transform = NullTransform()
        
        # Generic chains for attaching post-processing functions
        self._program.add_chain('vert_post_hook')
        self._program.add_chain('frag_color')
        
        # Components for plugging different types of position and color input.
        self._pos_component = None
        self._color_component = None
        self.pos_component = XYZPosComponent()
        self._frag_components = []
        self.fragment_components = [UniformColorComponent()]
        
        glopts = kwds.pop('gl_options', 'opaque')
        self.set_gl_options(glopts)
        
        if kwds:
            self.set_data(**kwds)

    def set_data(self, pos=None, faces=None, z=0.0, color=(1,1,1,1)):
        """
        *pos* must be array of shape (..., 2) or (..., 3).
        *z* is only used in the former case.
        
        *faces* is not supported yet.
        """
        # select input component based on pos.shape
        if pos is not None:
            if pos.shape[-1] == 2:
                if not isinstance(self.pos_component, XYPosComponent):
                    self.pos_component = XYPosComponent()
                self.pos_component.set_data(xy=pos, z=z, faces=faces)
            elif pos.shape[-1] == 3:
                if not isinstance(self.pos_component, XYZPosComponent):
                    self.pos_component = XYZPosComponent()
                self.pos_component.set_data(pos=pos, faces=faces)
            
        if isinstance(color, tuple):
            self.fragment_components = [UniformColorComponent(color)]
        elif isinstance(color, np.ndarray):
            self.fragment_components = [VertexColorComponent(color)]
            

    def paint(self):
        super(MeshVisual, self).paint()
        
        modes = set(self.pos_component.supported_draw_modes)
        for comp in self._frag_components:
            modes &= set(comp.supported_draw_modes)
        
        if len(modes) == 0:
            for c in self._frag_components:
                print(c, c.supported_draw_modes)
            raise Exception("Visual cannot paint--no mutually supported "
                            "draw modes between components.")
        
        #TODO: pick most efficient draw mode!
        mode = list(modes)[0]
            
        # activate all components
        self.pos_component.activate(self._program, mode)
        for comp in self._frag_components:
            comp.activate(self._program, mode)
        
        # TODO: this must be optimized.
        self._program['map_local_to_nd'] = self.transform.shader_map()
        
        self._program.draw(gloo.gl.GL_TRIANGLES, self.pos_component.index)

    @property
    def pos_component(self):
        return self._pos_component

    @pos_component.setter
    def pos_component(self, component):
        if self._pos_component is not None:
            self._pos_component._detach(self)
            self._pos_component = None
        component._attach(self)
        self._pos_component = component
        self.events.update()
        
    @property
    def fragment_components(self):
        return self._frag_components[:]
    
    @fragment_components.setter
    def fragment_components(self, comps):
        for comp in self._frag_components:
            comp._detach()
        self._frag_components = comps
        for comp in self._frag_components:
            comp._attach(self)
        self.events.update()
