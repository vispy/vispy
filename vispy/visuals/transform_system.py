# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from .transforms import NullTransform, STTransform


class TransformSystem(object):
    """ TransformSystem encapsulates information about the coordinate
    systems needed to draw a Visual.
    
    Visual rendering operates in four coordinate systems:
    
    * **Visual** - arbitrary local coordinate frame of the visual. Vertex 
      buffers used by the visual are usually specified in this coordinate
      system.
    * **Document** - This coordinate system has units of _logical_ pixels, and
      should usually represent the pixel coordinates of the canvas being drawn
      to. Visuals use this coordinate system to make measurements for font
      size, line width, and in general anything that is specified in physical
      units (px, pt, mm, in, etc.). Note that, by convention, _logical_ pixels
      are not necessarily the same size as the _physical_ pixels in the 
      framebuffer that is being rendered to.
    * **Buffer** - The buffer coordinate system has units of _physical_ pixels,
      and should usually represent the coordinates of the current framebuffer
      being rendered to. Visuals use this coordinate system primarily for
      antialiasing calculations. In most cases, this will have the same scale 
      as the document coordinate system
      because the active framebuffer is the back buffer of the canvas, and the 
      canvas will have _logical_ and _physical_ pixels of the same size. In the
      case of high-resolution displays, or when rendering to an off-screen 
      framebuffer with different scaling or boundaries than the canvas. 
    * **Render** - This coordinate system is the obligatory system for 
      vertexes returned by a vertex shader. It has coordinates (-1, -1) to 
      (1, 1) across the current glViewport. In OpenGL terminology, this is 
      called normalized device coordinates.

    Parameters
    ----------
    
    canvas : Canvas
        The canvas being drawn to.
    dpi : float 
        The dot-per-inch resolution of the document coordinate system. By 
        default this is set to the resolution of the canvas.
        
    Notes
    -----
    
    By default, TransformSystems are configured such that the document 
    coordinate system matches the logical pixels of the canvas, 

    Examples of use by Visuals
    --------------------------
    
    1. To convert local vertex coordinates to normalized device coordinates in 
    the vertex shader, we first need a vertex shader that supports configurable
    transformations::
    
        vec4 a_position;
        void main() {
            gl_Position = $transform(a_position);
        }
        
    Next, we supply the complete chain of transforms when drawing the visual:
    
        def draw(tr_sys):
            self.program['transform'] = tr_sys.get_full_transform()
            self.program['a_position'] = self.vertex_buffer
            self.program.draw('triangles')
    
    2. Draw a visual with 2 mm line width.

    3. Draw a triangle with antialiasing at the edge.
    
    4. Using inverse transforms in the fragment shader

    Examples of creating TransformSystem instances
    ----------------------------------------------
    
    1. Basic example, including checks for canvas resolution
    
    2. How to handle off-screen framebuffers
    
    """

    def __init__(self, canvas, dpi=72):
        self._canvas = canvas
        self._dpi = dpi
        
        # Null by default; visuals draw directly to the document coordinate
        # system.
        self._visual_to_document = NullTransform()
        
        # By default, this should invert the y axis -- no difference between 
        # the scale of logical and physical pixels.
        map_from = [(0, 0), canvas.size]
        map_to = [(0, canvas.size[1]), (canvas.size[0], 0)]
        self._document_to_buffer = STTransform.from_mapping(map_from, map_to)
        
        # Automatically configure buffer coordinate system to match the canvas 
        map_from = [(0, 0), canvas.size]
        map_to = [(-1, -1), (1, 1)]
        self._buffer_to_render = STTransform.from_mapping(map_from, map_to)
        

    @property
    def canvas(self):
        """ The Canvas being drawn to.
        """
        return self._canvas

    @property
    def dpi(self):
        """ Physical resolution of the document coordinate system (dots per
        inch).
        """
        return self._dpi

    @dpi.setter
    def dpi(self, dpi):
        self._dpi = dpi

    @property
    def visual_to_document(self):
        """ Transform mapping from visual local coordinate frame to document
        coordinate frame.
        """
        return self._visual_to_document
        
    @visual_to_document.setter
    def visual_to_document(self, tr):
        self._visual_to_document = tr
        
    @property
    def document_to_buffer(self):
        """ Transform mapping from document coordinate frame to the framebuffer
        (physical pixel) coordinate frame.
        """
        return self._document_to_buffer
        
    @document_to_buffer.setter
    def document_to_buffer(self, tr):
        self._document_to_buffer = tr
        
    @property
    def buffer_to_render(self):
        """ Transform mapping from pixel coordinate frame to rendering
        coordinate frame.
        """
        return self._pixel_to_render

    @buffer_to_render.setter
    def buffer_to_render(self, tr):
        self._buffer_to_render = tr

    def get_full_transform(self):
        """ Convenience method that returns the composition of all three
        transforms::
        
            buffer_to_render * document_to_buffer * visual_to_document
        
        This is used for visuals that do not require physical measurements
        or antialiasing.
        """
        return (self.buffer_to_render * 
                self.doc_to_buffer *
                self.visual_to_doc)
