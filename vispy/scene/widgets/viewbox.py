# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .widget import Widget
from ..subscene import SubScene
from ..cameras import make_camera, BaseCamera
from ...ext.six import string_types
from ... color import Color
from ... import gloo


class ViewBox(Widget):
    """ Provides a rectangular widget to which its subscene is rendered.
    
    Three classes work together when using a ViewBox:
    * The :class:`SubScene` class describes a "world" coordinate system and the
    entities that live inside it. 
    * ViewBox is a "window" through which we view the
    subscene. Multiple ViewBoxes may view the same subscene.
    * :class:`Camera` describes both the perspective from which the 
    subscene is rendered, and the way user interaction affects that 
    perspective. 
    
    In general it is only necessary to create the ViewBox; a SubScene and 
    Camera will be generated automatically.
    
    Parameters
    ----------
    camera : None, :class:`Camera`, or str
        The camera through which to view the SubScene. If None, then a 
        PanZoomCamera (2D interaction) is used. If str, then the string is
        used as the argument to :func:`make_camera`.
    scene : None or :class:`SubScene`
        The :class:`SubScene` instance to view. If None, a new 
        :class:`SubScene` is created.
    
    All extra keyword arguments are passed to :func:`Widget.__init__`.
    """
    def __init__(self, camera=None, scene=None, bgcolor='black', **kwds):
        
        self._camera = None
        self._bgcolor = Color(bgcolor).rgba
        Widget.__init__(self, **kwds)

        # Init preferred method to provided a pixel grid
        self._clip_method = 'viewport'

        # Each viewbox has a scene widget, which has a transform that
        # represents the transformation imposed by camera.
        if scene is None:
            self._scene = SubScene()
        elif isinstance(scene, SubScene):
            self._scene = scene
        else:
            raise TypeError('Argument "scene" must be None or SubScene.')
        self._scene.add_parent(self)
        
        # Camera is a helper object that handles scene transformation
        # and user interaction.
        if camera is None:
            camera = 'panzoom'
        if isinstance(camera, string_types):
            self.camera = make_camera(camera)
        elif isinstance(camera, BaseCamera):
            self.camera = camera
        else:
            raise TypeError('Argument "camera" must be None, str, or Camera.')

    @property
    def camera(self):
        """ The Camera in use by this ViewBox. 
        """
        return self._camera
    
    @camera.setter
    def camera(self, cam):
        if self._camera is not None:
            self._camera.viewbox = None
        self._camera = cam
        cam.viewbox = self
        
    def set_camera(self, cam_type, *args, **kwds):
        """ Create a new Camera and attach it to this ViewBox. 
        
        See :func:`make_camera` for arguments.
        """
        self.camera = make_camera(cam_type, *args, **kwds)
        return self.camera

    @property
    def scene(self):
        """ The root entity of the scene viewed by this ViewBox.
        """
        return self._scene

    def add(self, entity):
        """ Add an Entity to the scene for this ViewBox. 
        
        This is a convenience method equivalent to 
        `entity.add_parent(viewbox.scene)`
        """
        entity.add_parent(self.scene)

    @property
    def clip_method(self):
        """ The method used to clip the subscene to the boundaries of the 
        viewbox.

        Clipping methods are:
        
        * None - do not perform clipping. The default for now.
        * 'viewport' - use glViewPort to provide a clipped sub-grid
          onto the parent pixel grid, if possible.
        * 'fbo' - use an FBO to draw the subscene to a texture, and
          then render the texture in the parent scene.
        * 'fragment' - clipping in the fragment shader TODO
        * 'stencil' - TODO

        Notes
        -----
        The 'viewport' method requires that the transformation (from
        the pixel grid to this viewbox) is translate+scale only. If
        this is not the case, the method falls back to the default.

        The 'fbo' method is convenient when the result of the viewbox
        should be reused. Otherwise the overhead can be significant and
        the image can get slightly blurry if the transformations do
        not match.

        It is possible to have a graph with multiple stacked viewboxes
        which each use different methods (subject to the above
        restrictions).

        """
        return self._clip_method

    @clip_method.setter
    def clip_method(self, value):
        valid_methods = (None, 'fragment', 'viewport', 'fbo')
        if value not in valid_methods:
            t = 'clip_method should be in %s' % str(valid_methods)
            raise ValueError((t + ', not %r') % value)
        self._clip_method = value

    def draw(self, event):
        """ Draw the viewbox border/background, and prepare to draw the 
        subscene using the configured clipping method.
        """
        # todo: we could consider including some padding
        # so that we have room *inside* the viewbox to draw ticks and stuff
        
        # -- Calculate resolution
        
        # Get current transform and calculate the 'scale' of the viewbox
        size = self.size
        transform = event.document_transform()
        p0, p1 = transform.map((0, 0)), transform.map(size)
        res = (p1 - p0)[:2]
        res = abs(res[0]), abs(res[1])

        # Set resolution (note that resolution can be non-integer)
        self._resolution = res
        
        # -- Get user clipping preference

        prefer = self.clip_method
        viewport, fbo = None, None

        if prefer is None:
            pass
        elif prefer == 'fragment':
            raise NotImplementedError('No fragment shader clipping yet.')
        elif prefer == 'stencil':
            raise NotImplementedError('No stencil buffer clipping yet.')
        elif prefer == 'viewport':
            viewport = self._prepare_viewport(event)
        elif prefer == 'fbo':
            fbo = self._prepare_fbo(event)

        # -- Draw
        super(ViewBox, self).draw(event)

        event.push_viewbox(self)

        if fbo:
            # Ask the canvas to activate the new FBO
            offset = event.canvas_transform().map((0, 0))[:2]
            size = event.canvas_transform().map(self.size)[:2] - offset
            
            # Draw subscene to FBO
            event.push_fbo(fbo, offset, size)
            event.push_entity(self.scene)
            try:
                gloo.clear(color=self._bgcolor, depth=True)
                self.scene.draw(event)
            finally:
                event.pop_entity()
                event.pop_fbo()
            
            gloo.set_state(cull_face=False)
            self._myprogram.draw('triangle_strip')
        elif viewport:
            # Push viewport, draw, pop it
            event.push_viewport(viewport)
            event.push_entity(self.scene)
            try:
                self.scene.draw(event)
            finally:
                event.pop_entity()
                event.pop_viewport()

        else:
            # Just draw
            # todo: invoke fragment shader clipping
            self.scene.draw(event)

        event.pop_viewbox()

    def _prepare_viewport(self, event):
        p1 = event.map_to_framebuffer((0, 0))
        p2 = event.map_to_framebuffer(self.size)
        return p1[0], p1[1], p2[0]-p1[0], p2[1]-p1[1]

    def _prepare_fbo(self, event):
        """ Draw the viewbox via an FBO. This method can be applied
        in any situation, regardless of the transformations to this
        viewbox.

        TODO:
        Right now, this implementation create a program, texture and FBO
        on *each* draw, because it does not work otherwise. This is probably
        a bug in gloo that prevents using two FBO's / programs at the same
        time.

        Also, we use plain gloo and calculate the transformation
        ourselves, assuming 2D only. Eventually we should just use the
        transform of self. I could not get that to work, probably
        because I do not understand the component system yet.
        """

        from vispy.gloo import gl
        from vispy import gloo

        render_vertex = """
            attribute vec3 a_position;
            attribute vec2 a_texcoord;
            varying vec2 v_texcoord;
            void main()
            {
                gl_Position = vec4(a_position, 1.0);
                v_texcoord = a_texcoord;
            }
        """

        render_fragment = """
            uniform sampler2D u_texture;
            varying vec2 v_texcoord;
            void main()
            {
                vec4 v = texture2D(u_texture, v_texcoord);
                gl_FragColor = vec4(v.rgb, 1.0);
            }
        """

        # todo: don't do this on every draw
        if True:
            # Create program
            self._myprogram = gloo.Program(render_vertex, render_fragment)
            # Create texture
            self._tex = gloo.Texture2D(shape=(10, 10, 4), dtype=np.uint8)
            self._tex.interpolation = gl.GL_LINEAR
            self._myprogram['u_texture'] = self._tex
            # Create texcoords and vertices
            # Note y-axis is inverted here because the viewbox coordinate
            # system has origin in the upper-left, but the image is rendered
            # to the framebuffer with origin in the lower-left.
            texcoord = np.array([[0, 1], [1, 1], [0, 0], [1, 0]],
                                dtype=np.float32)
            position = np.zeros((4, 3), np.float32)
            self._myprogram['a_texcoord'] = gloo.VertexBuffer(texcoord)
            self._myprogram['a_position'] = self._vert = \
                gloo.VertexBuffer(position)

        # Get fbo, ensure it exists
        fbo = getattr(self, '_fbo', None)
        if True:  # fbo is None:
            self._fbo = 4
            self._fbo = fbo = gloo.FrameBuffer(self._tex,
                                               depth=gloo.DepthBuffer((10,
                                                                       10)))

        # Set texture coords to make the texture be drawn in the right place
        # Note that we would just use -1..1 if we would use a Visual.
        coords = [[0, 0], [self.size[0], self.size[1]]]
        
        transform = event.render_transform  # * self.scene.viewbox_transform
        coords = transform.map(coords)
        x1, y1, z = coords[0][:3]
        x2, y2, z = coords[1][:3]
        vertices = np.array([[x1, y1, z], [x2, y1, z],
                             [x1, y2, z], [x2, y2, z]],
                            np.float32)
        self._vert.set_data(vertices)

        # Set fbo size (mind that this is set using shape!)
        resolution = [int(i+0.5) for i in self._resolution]  # set in draw()
        shape = resolution[1], resolution[0]
        fbo.color_buffer.resize(shape+(4,))
        fbo.depth_buffer.resize(shape)

        return fbo
