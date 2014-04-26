# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division, print_function

import numpy as np

from ... import gloo
from ...util import event
from ...util.six import string_types

from ..shaders import ModularProgram, Function
from ..transforms import NullTransform
from ..entity import Entity
from ..components import (VisualComponent, XYPosComponent, XYZPosComponent, 
                         UniformColorComponent, VertexColorComponent)

"""
API Issues to work out:

  * Need Visual.bounds() as described here:
    https://github.com/vispy/vispy/issues/141

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
        
  - Make base shaders look like:
       vertex_input => vertex_adjustment, transform_to_nd, post_hook
       color_input => color_adjustment
        
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



# Commonly-used GL option groups.
GLOptions = {
    'opaque': {
        'GL_DEPTH_TEST': True,
        'GL_BLEND': False,
        #'GL_ALPHA_TEST': False,
        'GL_CULL_FACE': False,
    },
    'translucent': {
        'GL_DEPTH_TEST': True,
        'GL_BLEND': True,
        #'GL_ALPHA_TEST': False,
        'GL_CULL_FACE': False,
        'glBlendFunc': ('GL_SRC_ALPHA', 'GL_ONE_MINUS_SRC_ALPHA'),
    },
    'additive': {
        'GL_DEPTH_TEST': False,
        'GL_BLEND': True,
        #'GL_ALPHA_TEST': False,
        'GL_CULL_FACE': False,
        'glBlendFunc': ('GL_SRC_ALPHA', 'GL_ONE'),
    },
}    


class Visual(Entity):
    """ 
    Abstract class representing a drawable object. Visuals implement the 
    following interfaces:
    
        * paint() calls all of the GL commands necessary to paint the visual.
        * bounds() describes the bounding rectangle of the visual.
        * gl_options() is used to configure the OpenGL state immediately
          before the visual is painted.
          
    
    Events:
    
    update : Event
        Emitted when the visual has changed and needs to be repainted.
    bounds_change : Event
        Emitted when the bounding rectangle of the visual has changed.
    """
    
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

    
    
    def __init__(self, parents=None):
        Entity.__init__(self, parents)
        
        # Dict of {'GL_FLAG': bool} and {'glFunctionName': (args)} 
        # specifications. By default, these are enabled whenever the Visual 
        # if painted. This provides a simple way for the user to customize the
        # appearance of the Visual. Example:
        # 
        #     { 'GL_BLEND': True,
        #       'glBlendFunc': ('GL_SRC_ALPHA', 'GL_ONE') }
        # 
        self._gl_options = {}
        
        # Add event for bounds changing
        self.events.add(bounds_change=event.Event)
        
        self._program = ModularProgram(self.VERTEX_SHADER, 
                                       self.FRAGMENT_SHADER)
        
        # Generic chains for attaching post-processing functions
        self._program.add_chain('local_position')
        self._program.add_chain('vert_post_hook')
        self._program.add_chain('frag_color')
        
        # Cache of the total transform chain to get here ...
        self._total_transform = None
        
        # Components for plugging different types of position and color input.
        self._pos_components = []
        #self._color_component = None
        #self.pos_component = XYZPosComponent()
        self._color_components = []
        #self.color_components = [UniformColorComponent()]
        
    
    @property
    def primitive(self):
        """
        The GL primitive used to draw this visual.
        """
        return gloo.gl.GL_TRIANGLES
    
    @property
    def vertex_index(self):
        """
        Returns the IndexBuffer (or None) that should be used when drawing 
        this Visual.        
        """
        # TODO: What to do here? How do we decide which component should 
        # generate the index?
        return self.pos_components[0].index

    def set_data(self, pos=None, index=None, z=0.0, color=None):
        """
        Default set_data implementation is only used for a few visuals..
        *pos* must be array of shape (..., 2) or (..., 3).
        *z* is only used in the former case.
        """
        # select input component based on pos.shape
        if pos is not None:
            if pos.shape[-1] == 2:
                comp = XYPosComponent(xy=pos, z=z, index=index)
                self.pos_components = [comp]
            elif pos.shape[-1] == 3:
                comp = XYZPosComponent(pos=pos, index=index)
                self.pos_components = [comp]
            else:
                raise Exception("Can't handle position data: %s" % pos)
        
        if color is not None:
            if isinstance(color, tuple):
                self.color_components = [UniformColorComponent(color)]
            elif isinstance(color, np.ndarray):
                self.color_components = [VertexColorComponent(color)]
            else:
                raise Exception("Can't handle color data:")
        
    def set_gl_options(self, default=None, **opts):
        """
        Set all GL options for this Visual. 
        Keyword arguments must be one of two formats:
        
        * GL_FLAG=bool
        * glFunctionName=(args)
        
        These options are invoked every time the Visual is drawn.
        Optionally, *default* gives the name of a pre-set collection of options
        from the GLOptions global.
        """
        if default is not None:
            opts = GLOptions[default]
        self._gl_options = opts
        
    def update_gl_options(self, default=None, **opts):
        """
        Update GL options rather than replacing all. See set_gl_options().
        
        Optionally, *default* gives the name of a pre-set collection of options
        from the GLOptions global.
        """
        if default is not None:
            opts = GLOptions[default]
        self._gl_options.update(opts)
        
    def gl_options(self):
        """
        Return a dict describing the GL options in use for this Visual. 
        See set_gl_options().
        """
        return self._gl_options.copy()

    @property
    def pos_components(self):
        return self._pos_components[:]
    
    @pos_components.setter
    def pos_components(self, comps):
        for comp in self._pos_components:
            try:
                comp._detach()
            except:
                print(comp)
                raise
        self._pos_components = comps
        for comp in self._pos_components:
            comp._attach(self)
        self.events.update()

    @property
    def color_components(self):
        return self._color_components[:]
    
    @color_components.setter
    def color_components(self, comps):
        for comp in self._color_components:
            try:
                comp._detach()
            except:
                print(comp)
                raise
        self._color_components = comps
        for comp in self._color_components:
            comp._attach(self)
        self.events.update()

    def update(self):
        """
        This method is called whenever the Visual must be repainted.
        
        """
        self.events.update()
    
# no need if we use the drawing system
#     def on_paint(self, event):
#         """ when we get a paint event from the scenegraph
#         """
#         self._visual.transform = event.viewport_transform
#         self.paint()
    
    def paint(self):
        """
        Paint this visual now.
        
        The default implementation configures GL flags according to the contents
        of self._gl_options            
        
        """
        print('paint', self)
        self._activate_gl_options()
        mode = self._paint_mode()
        self._activate_components(mode)
        self._program.draw(self.primitive, self.vertex_index)

    def _paint_mode(self):
        """
        Return the mode that should be used to paint this visual
        (DRAW_PRE_INDEXED or DRAW_UNINDEXED)
        """
        modes = set([VisualComponent.DRAW_PRE_INDEXED, 
                     VisualComponent.DRAW_UNINDEXED])
        for comp in self._color_components + self.pos_components:
            modes &= comp.supported_draw_modes
        
        if len(modes) == 0:
            for c in self._color_components:
                print(c, c.supported_draw_modes)
            raise Exception("Visual cannot paint--no mutually supported "
                            "draw modes between components.")
        
        #TODO: pick most efficient draw mode!
        return list(modes)[0]
    
    def _activate_gl_options(self):
        for name, val in self._gl_options.items():
            if isinstance(val, bool):
                flag = getattr(gloo.gl, name)
                if val:
                    gloo.gl.glEnable(flag)
                else:
                    gloo.gl.glDisable(flag)
            else:
                args = []
                for arg in val:
                    if isinstance(arg, string_types):
                        arg = getattr(gloo.gl, arg)
                    args.append(arg)
                func = getattr(gloo.gl, name)
                func(*args)
                
    def _activate_components(self, mode):
        """
        This is called immediately before painting to inform all components
        that a paint is about to occur and to let them assign program
        variables.
        """
        if len(self._pos_components) == 0:
            raise Exception("Cannot draw visual %s; no position components" 
                            % self)
        if len(self._color_components) == 0:
            raise Exception("Cannot draw visual %s; no color components"
                            % self)
        comps = self._pos_components + self._color_components
        all_comps = set(comps)
        while len(comps) > 0:
            comp = comps.pop(0)
            comps.extend(comp._deps)
            all_comps |= set(comp._deps)
        
        for comp in all_comps:
            comp.activate(self._program, mode)
            
        self._activate_transform()
        
    def _activate_transform(self):
        # TODO: this must be optimized.
        #self._program['map_local_to_nd'] = self.transform.shader_map()
        self._program['map_local_to_nd'] = self._total_transform.shader_map()
        


