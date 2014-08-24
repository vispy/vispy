# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division, print_function

import numpy as np

from ... import gloo
from .visual import Visual
from ..shaders import ModularProgram, Variable
from ..components import (VisualComponent, XYPosComponent, XYZPosComponent,
                          UniformColorComponent, VertexColorComponent)

"""
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
            

class ModularVisual(Visual):
    """
    Abstract modular visual. This extends Visual by implementing a system
    of attachable components that change the input and output behaviors of
    the visual. 

    * A modular GLSL program with a standard set of vertex and
      fragment shader hooks
    * A mechanism for adding and removing components
      that affect the vertex position (pos_components) and fragment
      color (color_components)
    * A default draw() method that:
        * activates each of the attached components
        * negotiates a buffer mode (pre-indexed or unindexed) supported by
          all components
        * Requests an index buffer from components (if needed)
        * Instructs the program to draw using self.primitive
    * A simple set_data() method intended to serve as an example for
      subclasses to follow.

    """

    VERTEX_SHADER = """
    void main(void) {
        $local_pos = $local_position();
        vec4 nd_pos = $map_local_to_nd($local_pos);
        gl_Position = nd_pos;

        $vert_post_hook();
    }
    """

    FRAGMENT_SHADER = """
    // Fragment shader consists of only a single hook that is usually defined
    // by a chain of functions, each which sets or modifies the curren
    // fragment color, or discards it.
    void main(void) {
        gl_FragColor = $frag_color();
    }
    """

    def __init__(self, **kwargs):
        Visual.__init__(self, **kwargs)
        
        # Dict of {'GL_FLAG': bool} and {'glFunctionName': (args)} 
        # specifications. By default, these are enabled whenever the Visual 
        # is drawn. This provides a simple way for the user to customize the
        # appearance of the Visual. Example:
        #
        #     { 'GL_BLEND': True,
        #       'glBlendFunc': ('GL_SRC_ALPHA', 'GL_ONE') }
        #
        self._gl_options = [None, {}]

        self._program = ModularProgram(self.VERTEX_SHADER,
                                       self.FRAGMENT_SHADER)
        self._program.changed.connect(self._program_changed)
        
        self._program.vert['local_pos'] = Variable('local_pos', 
                                                   vtype='', dtype='vec4')
        
        # Generic chains for attaching post-processing functions
        self._program.vert.add_chain('local_position')
        self._program.vert.add_chain('vert_post_hook')
        self._program.frag.add_chain('frag_color')

        # Components for plugging different types of position and color input.
        self._pos_components = []
        #self._color_component = None
        #self.pos_component = XYZPosComponent()
        self._color_components = []
        #self.color_components = [UniformColorComponent()]

        # Primitive, default is GL_TRIANGLES
        self._primitive = gloo.gl.GL_TRIANGLES
    
    @property
    def primitive(self):
        """
        The GL primitive used to draw this visual.
        """
        return self._primitive

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
                comp = XYPosComponent(xy=pos.astype(np.float32), 
                                      z=z, index=index)
                self.pos_components = [comp]
            elif pos.shape[-1] == 3:
                comp = XYZPosComponent(pos=pos.astype(np.float32), index=index)
                self.pos_components = [comp]
            else:
                raise Exception("Can't handle position data: %s" % pos)

        if color is not None:
            if isinstance(color, tuple):
                self.color_components = [UniformColorComponent(color)]
            elif isinstance(color, np.ndarray):
                if color.ndim == 1:
                    self.color_components = [UniformColorComponent(color)]
                elif color.ndim > 1:
                    self.color_components = [VertexColorComponent(color)]
            else:
                raise Exception("Can't handle color data: %r" % color)

    def set_gl_options(self, default=-1, **kwds):
        """
        Set all GL options for this Visual. Most common arguments are 
        'translucent', 'opaque', and 'additive'.
        See gloo.set_state() for more information.

        These options are invoked every time the Visual is drawn.
        """
        if default is not -1:
            self._gl_options[0] = default
        self._gl_options[1] = kwds

    def update_gl_options(self, default=-1, **kwds):
        """
        Update GL options rather than replacing all. See set_gl_options().
        """
        if default is not -1:
            self._gl_options[0] = default
        self._gl_options.update(kwds)

    def gl_options(self):
        """
        Return the GL options in use for this Visual.
        See set_gl_options().
        """
        return self._gl_options[0], self._gl_options[1].copy()

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
        This method is called whenever the Visual must be redrawn.

        """
        self.events.update()

# no need if we use the drawing system
#     def on_draw(self, event):
#         """ when we get a draw event from the scenegraph
#         """
#         self._visual.transform = event.viewport_transform
#         self.draw()

    def draw(self, event):
        """
        Draw this visual now.

        The default implementation configures GL flags according to the
        contents of self._gl_options

        """
        self._activate_gl_options()
        mode = self._draw_mode()
        self._activate_components(mode, event)
        self._program.draw(self.primitive, self.vertex_index)

    # todo: should this be called "buffer_mode" ?
    def _draw_mode(self):
        """
        Return the mode that should be used to draw this visual
        (DRAW_PRE_INDEXED or DRAW_UNINDEXED)
        """
        modes = set([VisualComponent.DRAW_PRE_INDEXED,
                     VisualComponent.DRAW_UNINDEXED])
        for comp in (self._color_components + self.pos_components):
            modes &= comp.supported_draw_modes

        if len(modes) == 0:
            for c in self._color_components:
                print(c, c.supported_draw_modes)
            raise Exception("Visual cannot draw--no mutually supported "
                            "draw modes between components.")

        #TODO: pick most efficient draw mode!
        return list(modes)[0]

    def _activate_gl_options(self):
        gloo.set_state(self._gl_options[0], **self._gl_options[1])

    def _activate_components(self, mode, event):
        """
        This is called immediately before drawing to inform all components
        that a draw is about to occur and to let them assign program
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

        self._activate_transform(event)
        
        for comp in all_comps:
            comp.activate(self._program, mode)

    def _activate_transform(self, event):
        # TODO: this must be optimized.
        # Allow using as plain visual or in a scenegraph
        t = event.render_transform.shader_map()
        self._program.vert['map_local_to_nd'] = t

    def _program_changed(self, event):
        self.update()
