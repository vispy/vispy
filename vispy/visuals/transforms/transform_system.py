# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from .linear import STTransform, NullTransform
from .chain import ChainTransform
from ._util import TransformCache
from ...util.event import EventEmitter


class TransformSystem(object):
    """ TransformSystem encapsulates information about the coordinate
    systems needed to draw a Visual.

    Visual rendering operates in six coordinate systems:

    * **Visual** - arbitrary local coordinate frame of the visual. Vertex
      buffers used by the visual are usually specified in this coordinate
      system.

    * **Scene** - This is an isometric coordinate system used mainly for 
      lighting calculations.

    * **Document** - This coordinate system has units of _logical_ pixels, and
      should usually represent the pixel coordinates of the canvas being drawn
      to. Visuals use this coordinate system to make measurements for font
      size, line width, and in general anything that is specified in physical
      units (px, pt, mm, in, etc.). In most circumstances, this is exactly the
      same as the canvas coordinate system.

    * **Canvas** - This coordinate system represents the logical pixel
      coordinates of the canvas. It has its origin in the top-left corner of
      the canvas, and is typically the coordinate system that mouse and touch 
      events are reported in. Note that, by convention, _logical_ pixels
      are not necessarily the same size as the _physical_ pixels in the
      framebuffer that is being rendered to.

    * **Framebuffer** - The buffer coordinate system has units of _physical_ 
      pixels, and should usually represent the coordinates of the current 
      framebuffer (on the canvas or an FBO) being rendered to. Visuals use this
      coordinate system primarily for antialiasing calculations. It is also the
      coorinate system used by glFragCoord. In most cases,
      this will have the same scale as the document and canvas coordinate 
      systems because the active framebuffer is the
      back buffer of the canvas, and the canvas will have _logical_ and
      _physical_ pixels of the same size. However, the scale may be different
      in the case of high-resolution displays, or when rendering to an 
      off-screen framebuffer with different scaling or boundaries than the
      canvas.

    * **Render** - This coordinate system is the obligatory system for
      vertices returned by a vertex shader. It has coordinates (-1, -1) to
      (1, 1) across the current glViewport. In OpenGL terminology, this is
      called clip coordinates.

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
            doc_to_render = (tr_sys.framebuffer_transform *
                             tr_sys.document_transform)
            self.program['visual_to_doc'] = doc_to_render.shader_map()

            self.program['u_line_width'] = self.line_width
            self.program['u_dpi'] = tr_sys.dpi
            self.program['a_position'] = self.vertex_buffer
            self.program['a_normal'] = self.normal_buffer
            self.program.draw('triangles')

    3. Draw a triangle with antialiasing at the edge.

    4. Using inverse transforms in the fragment shader
    """

    def __init__(self, canvas=None, dpi=None):
        self.changed = EventEmitter(source=self, type='transform_changed')
        self._canvas = None
        self._fbo_bounds = None
        self.canvas = canvas
        self._cache = TransformCache()
        self._dpi = dpi

        # Assign a ChainTransform for each step. This allows us to always
        # return the same transform objects regardless of how the user
        # configures the system.
        self._visual_transform = ChainTransform([NullTransform()])
        self._scene_transform = ChainTransform([NullTransform()])
        self._document_transform = ChainTransform([NullTransform()])
        self._canvas_transform = ChainTransform([STTransform(),
                                                 STTransform()])
        self._framebuffer_transform = ChainTransform([STTransform()])
        
        for tr in (self._visual_transform, self._scene_transform, 
                   self._document_transform, self._canvas_transform,
                   self._framebuffer_transform):
            tr.changed.connect(self.changed)

    def configure(self, viewport=None, fbo_size=None, fbo_rect=None,
                  canvas=None):
        """Automatically configure the TransformSystem:

        * canvas_transform maps from the Canvas logical pixel
          coordinate system to the framebuffer coordinate system, taking into 
          account the logical/physical pixel scale factor, current FBO 
          position, and y-axis inversion.
        * framebuffer_transform maps from the current GL viewport on the
          framebuffer coordinate system to clip coordinates (-1 to 1). 
          
          
        Parameters
        ==========
        viewport : tuple or None
            The GL viewport rectangle (x, y, w, h). If None, then it
            is assumed to cover the entire canvas.
        fbo_size : tuple or None
            The size of the active FBO. If None, then it is assumed to have the
            same size as the canvas's framebuffer.
        fbo_rect : tuple or None
            The position and size (x, y, w, h) of the FBO in the coordinate
            system of the canvas's framebuffer. If None, then the bounds are
            assumed to cover the entire active framebuffer.
        canvas : Canvas instance
            Optionally set the canvas for this TransformSystem. See the 
            `canvas` property.
        """
        # TODO: check that d2f and f2r transforms still contain a single
        # STTransform (if the user has modified these, then auto-config should
        # either fail or replace the transforms)
        if canvas is not None:
            self.canvas = canvas
        canvas = self._canvas
        if canvas is None:
            raise RuntimeError("No canvas assigned to this TransformSystem.")
       
        # By default, this should invert the y axis--canvas origin is in top
        # left, whereas framebuffer origin is in bottom left.
        map_from = [(0, 0), canvas.size]
        map_to = [(0, canvas.physical_size[1]), (canvas.physical_size[0], 0)]
        self._canvas_transform.transforms[1].set_mapping(map_from, map_to)

        if fbo_rect is None:
            self._canvas_transform.transforms[0].scale = (1, 1, 1)
            self._canvas_transform.transforms[0].translate = (0, 0, 0)
        else:
            # Map into FBO coordinates
            map_from = [(fbo_rect[0], fbo_rect[1]),
                        (fbo_rect[0] + fbo_rect[2], fbo_rect[1] + fbo_rect[3])]
            map_to = [(0, 0), fbo_size]
            self._canvas_transform.transforms[0].set_mapping(map_from,  map_to)
            
        if viewport is None:
            if fbo_size is None:
                # viewport covers entire canvas
                map_from = [(0, 0), canvas.physical_size]
            else:
                # viewport covers entire FBO
                map_from = [(0, 0), fbo_size]
        else:
            map_from = [viewport[:2], 
                        (viewport[0] + viewport[2], viewport[1] + viewport[3])]
        map_to = [(-1, -1), (1, 1)]
        self._framebuffer_transform.transforms[0].set_mapping(map_from, map_to)

    @property
    def canvas(self):
        """ The Canvas being drawn to.
        """
        return self._canvas
    
    @canvas.setter
    def canvas(self, canvas):
        self._canvas = canvas

    @property
    def dpi(self):
        """ Physical resolution of the document coordinate system (dots per
        inch).
        """
        if self._dpi is None:
            if self._canvas is None:
                return None
            else:
                return self.canvas.dpi
        else:
            return self._dpi

    @dpi.setter
    def dpi(self, dpi):
        assert dpi > 0
        self._dpi = dpi

    @property
    def visual_transform(self):
        """ Transform mapping from visual local coordinate frame to scene
        coordinate frame.
        """
        return self._visual_transform

    @visual_transform.setter
    def visual_transform(self, tr):
        self._visual_transform.transforms = tr

    @property
    def scene_transform(self):
        """ Transform mapping from scene coordinate frame to document
        coordinate frame.
        """
        return self._scene_transform

    @scene_transform.setter
    def scene_transform(self, tr):
        self._scene_transform.transforms = tr

    @property
    def document_transform(self):
        """ Transform mapping from document coordinate frame to the framebuffer
        (physical pixel) coordinate frame.
        """
        return self._document_transform

    @document_transform.setter
    def document_transform(self, tr):
        self._document_transform.transforms = tr

    @property
    def canvas_transform(self):
        """ Transform mapping from canvas coordinate frame to framebuffer
        coordinate frame.
        """
        return self._canvas_transform

    @canvas_transform.setter
    def canvas_transform(self, tr):
        self._canvas_transform.transforms = tr

    @property
    def framebuffer_transform(self):
        """ Transform mapping from pixel coordinate frame to rendering
        coordinate frame.
        """
        return self._framebuffer_transform

    @framebuffer_transform.setter
    def framebuffer_transform(self, tr):
        self._framebuffer_transform.transforms = tr

    def get_transform(self, map_from='visual', map_to='render'):
        """Return a transform mapping between any two coordinate systems.
        
        Parameters
        ----------
        map_from : str
            The starting coordinate system to map from. Must be one of: visual,
            scene, document, canvas, framebuffer, or render.
        map_to : str
            The ending coordinate system to map to. Must be one of: visual,
            scene, document, canvas, framebuffer, or render.
        """
        tr = ['visual', 'scene', 'document', 'canvas', 'framebuffer', 'render']
        ifrom = tr.index(map_from)
        ito = tr.index(map_to)
        
        if ifrom < ito:
            trs = [getattr(self, '_' + t + '_transform')
                   for t in tr[ifrom:ito]][::-1]
        else:
            trs = [getattr(self, '_' + t + '_transform').inverse
                   for t in tr[ito:ifrom]]
        return self._cache.get(trs)
    
    @property
    def pixel_scale(self):
        tr = self._canvas_transform
        return (tr.map((1, 0)) - tr.map((0, 0)))[0]
