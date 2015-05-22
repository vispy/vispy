# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from .linear import NullTransform, STTransform
from ._util import TransformCache


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
      as the document coordinate system because the active framebuffer is the
      back buffer of the canvas, and the canvas will have _logical_ and
      _physical_ pixels of the same size. The scale may be different in the
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

    Examples
    --------
    Use by Visuals
    ~~~~~~~~~~~~~~

    1. To convert local vertex coordinates to normalized device coordinates in
    the vertex shader, we first need a vertex shader that supports configurable
    transformations::

        vec4 a_position;
        void main() {
            gl_Position = $transform(a_position);
        }

    Next, we supply the complete chain of transforms when drawing the visual:

        def draw(tr_sys):
            tr = tr_sys.get_full_transform()
            self.program['transform'] = tr.shader_map()
            self.program['a_position'] = self.vertex_buffer
            self.program.draw('triangles')

    2. Draw a line whose width is given in mm. To start, we need normal vectors
    for each vertex, which tell us the direction the vertex should move in
    order to set the line width::

        vec4 a_position;
        vec4 a_normal;
        float u_line_width;
        float u_dpi;
        void main() {
            // map vertex position and normal vector to the document cs
            vec4 doc_pos = $visual_to_doc(a_position);
            vec4 doc_normal = $visual_to_doc(a_position + a_normal) - doc_pos;

            // Use DPI to convert mm line width to logical pixels
            float px_width = (u_line_width / 25.4) * dpi;

            // expand by line width
            doc_pos += normalize(doc_normal) * px_width;

            // finally, map the remainder of the way to normalized device
            // coordinates.
            gl_Position = $doc_to_render(a_position);
        }

    In this case, we need to access
    the transforms independently, so ``get_full_transform()`` is not useful
    here::

        def draw(tr_sys):
            # Send two parts of the full transform separately
            self.program['visual_to_doc'] = tr_sys.visual_to_doc.shader_map()
            doc_to_render = (tr_sys.framebuffer_to_render *
                             tr_sys.document_to_framebuffer)
            self.program['visual_to_doc'] = doc_to_render.shader_map()

            self.program['u_line_width'] = self.line_width
            self.program['u_dpi'] = tr_sys.dpi
            self.program['a_position'] = self.vertex_buffer
            self.program['a_normal'] = self.normal_buffer
            self.program.draw('triangles')

    3. Draw a triangle with antialiasing at the edge.

    4. Using inverse transforms in the fragment shader

    Creating TransformSystem instances
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    1. Basic example, including checks for canvas resolution

    2. How to handle off-screen framebuffers

    """

    def __init__(self, canvas, dpi=None):
        self._canvas = canvas
        self._cache = TransformCache()
        if dpi is None:
            dpi = canvas.dpi
        self._dpi = dpi

        # Null by default; visuals draw directly to the document coordinate
        # system.
        self._visual_to_document = NullTransform()
        self._document_to_framebuffer = STTransform()
        self._framebuffer_to_render = STTransform()

        self.auto_configure()

    def auto_configure(self):
        """Automatically configure the TransformSystem:

        * document_to_framebuffer maps from the Canvas logical pixel
          coordinate system to the framebuffer coordinate system, assuming
          physical pixels of the same size. The y-axis is inverted in this
          transform.
        * framebuffer_to_render maps from the framebuffer coordinate system to
          normalized device coordinates (-1 to 1).
        """
        # By default, this should invert the y axis -- no difference between
        # the scale of logical and physical pixels.
        canvas = self._canvas
        map_from = [(0, 0), canvas.size]
        map_to = [(0, canvas.size[1]), (canvas.size[0], 0)]
        self._document_to_framebuffer.set_mapping(map_from, map_to)

        # Automatically configure buffer coordinate system to match the canvas
        map_from = [(0, 0), canvas.size]
        map_to = [(-1, -1), (1, 1)]
        self._framebuffer_to_render.set_mapping(map_from, map_to)

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
        assert dpi > 0
        self._dpi = dpi

    @property
    def visual_to_document(self):
        """ Transform mapping from visual local coordinate frame to document
        coordinate frame.
        """
        return self._visual_to_document

    @visual_to_document.setter
    def visual_to_document(self, tr):
        if self._visual_to_document is not tr:
            self._visual_to_document = tr

    @property
    def document_to_framebuffer(self):
        """ Transform mapping from document coordinate frame to the framebuffer
        (physical pixel) coordinate frame.
        """
        return self._document_to_framebuffer

    @document_to_framebuffer.setter
    def document_to_framebuffer(self, tr):
        if self._document_to_framebuffer is not tr:
            self._document_to_framebuffer = tr

    @property
    def framebuffer_to_render(self):
        """ Transform mapping from pixel coordinate frame to rendering
        coordinate frame.
        """
        return self._framebuffer_to_render

    @framebuffer_to_render.setter
    def framebuffer_to_render(self, tr):
        if self._framebuffer_to_render is not tr:
            self._framebuffer_to_render = tr

    def get_full_transform(self):
        """ Convenience method that returns the composition of all three
        transforms::

            framebuffer_to_render * document_to_framebuffer * visual_to_document

        This is used for visuals that do not require physical measurements
        or antialiasing.
        """  # noqa
        return self._cache.get([self.framebuffer_to_render,
                                self.document_to_framebuffer,
                                self.visual_to_document])
