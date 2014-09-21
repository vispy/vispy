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
      antialiasing calculations. In most cases, this will be a null transform 
      because the framebuffer will be the back buffer of a canvas, and the 
      canvas will have _logical_ and _physical_ pixels of the same size. In the
      case of high-resolution displays, or when rendering to an off-screen 
      framebuffer with different scaling or boundaries than the canvas. 
    * **Render** - This coordinate system is the obligatory system for 
      vertexes returned by a vertex shader. It has coordinates (-1, -1) to 
      (1, 1) across the current glViewport. In OpenGL terminology, this is 
      called normalized device coordinates.

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
            self.program['transform'] = (tr_sys.buffer_to_render * 
                                         tr_sys.doc_to_buffer *
                                         tr_sys.visual_to_doc)
            self.program['a_position'] = self.vertex_buffer
            self.program.draw('triangles')
    
    2. Draw a visual with 2 mm line width.

    3. Draw a triangle with antialiasing at the edge.

    Examples of creating TransformSystem instances
    ----------------------------------------------
    
    1. Basic example, including checks for canvas resolution
    
    2. How to handle off-screen framebuffers
    
    """

    def __init__(self, canvas):
        self._canvas = canvas
        self._visual_to_document = NullTransform()
        self._document_to_buffer = NullTransform()
        self._buffer_to_render = STTransform()

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

    @property
    def visual_to_document(self):
        """ Transform mapping from visual local coordinate frame to document
        coordinate frame.
        """
        return self._visual_to_document
        
    @property
    def document_to_buffer(self):
        """ Transform mapping from document coordinate frame to the framebuffer
        (physical pixel) coordinate frame.
        """
        return self._document_to_buffer
        
    @property
    def buffer_to_render(self):
        """ Transform mapping from pixel coordinate frame to rendering
        coordinate frame.
        """
        return self._pixel_to_render
    