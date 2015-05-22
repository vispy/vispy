# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .widget import Widget
from ..subscene import SubScene
from ..cameras import make_camera, BaseCamera
from ...ext.six import string_types
from ... import gloo
from ...visuals.components import Clipper
from ...visuals import Visual


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
        The `SubScene` instance to view. If None, a new `SubScene` is created.
    clip_method : str
        Clipping method to use.
    **kwargs : dict
        Extra keyword arguments to pass to `Widget`.
    """
    def __init__(self, camera=None, scene=None, clip_method='fragment',
                 **kwargs):

        self._camera = None
        Widget.__init__(self, **kwargs)

        # Init method to provide a pixel grid
        self._clip_method = clip_method
        self._clipper = Clipper()

        # Each viewbox has a scene widget, which has a transform that
        # represents the transformation imposed by camera.
        if scene is None:
            if self.name is not None:
                name = str(self.name) + "_Scene"
            else:
                name = None
            self._scene = SubScene(name=name)
        elif isinstance(scene, SubScene):
            self._scene = scene
        else:
            raise TypeError('Argument "scene" must be None or SubScene.')
        self._scene.add_parent(self)

        # Camera is a helper object that handles scene transformation
        # and user interaction.
        if camera is None:
            camera = 'base'
        if isinstance(camera, string_types):
            self.camera = make_camera(camera, parent=self.scene)
        elif isinstance(camera, BaseCamera):
            self.camera = camera
        else:
            raise TypeError('Argument "camera" must be None, str, or Camera.')

    @property
    def camera(self):
        """ Get/set the Camera in use by this ViewBox

        If a string is given (e.g. 'panzoom', 'turntable', 'fly'). A
        corresponding camera is selected if it already exists in the
        scene, otherwise a new camera is created.

        The camera object is made a child of the scene (if it is not
        already in the scene).

        Multiple cameras can exist in one scene, although only one can
        be active at a time. A single camera can be used by multiple
        viewboxes at the same time.
        """
        return self._camera

    @camera.setter
    def camera(self, cam):
        if isinstance(cam, string_types):
            # Try to select an existing camera
            for child in self.scene.children:
                if isinstance(child, BaseCamera):
                    this_cam_type = child.__class__.__name__.lower()[:-6]
                    if this_cam_type == cam:
                        self.camera = child
                        return
            else:
                # No such camera yet, create it then
                self.camera = make_camera(cam)
            
        elif isinstance(cam, BaseCamera):
            # Ensure that the camera is in the scene
            if not self.is_in_scene(cam):
                cam.add_parent(self.scene)
            # Disconnect / connect
            if self._camera is not None:
                self._camera._viewbox_unset(self)
            self._camera = cam
            if self._camera is not None:
                self._camera._viewbox_set(self)
            # Update view
            cam.view_changed()
        
        else:
            raise ValueError('Not a camera object.')

    def is_in_scene(self, node):
        """Get whether the given node is inside the scene of this viewbox.

        Parameters
        ----------
        node : instance of Node
            The node.
        """
        def _is_child(parent, child):
            if child in parent.children:
                return True
            else:
                for c in parent.children:
                    if isinstance(c, ViewBox):
                        continue
                    elif _is_child(c, child):
                        return True
            return False
        
        return _is_child(self.scene, node)
    
    def get_scene_bounds(self, dim=None):
        """Get the total bounds based on the visuals present in the scene

        Parameters
        ----------
        dim : int | None
            Dimension to return.

        Returns
        -------
        bounds : list | tuple
            If ``dim is None``, Returns a list of 3 tuples, otherwise
            the bounds for the requested dimension.
        """
        # todo: handle sub-children
        # todo: handle transformations
        # Init
        mode = 'data'  # or visual?
        bounds = [(np.inf, -np.inf), (np.inf, -np.inf), (np.inf, -np.inf)]
        # Get bounds of all children
        for ob in self.scene.children:
            if hasattr(ob, 'bounds'):
                for axis in (0, 1, 2):
                    if (dim is not None) and dim != axis:
                        continue
                    b = ob.bounds(mode, axis)
                    if b is not None:
                        b = min(b), max(b)  # Ensure correct order
                        bounds[axis] = (min(bounds[axis][0], b[0]), 
                                        max(bounds[axis][1], b[1]))
        # Set defaults
        for axis in (0, 1, 2):
            if any(np.isinf(bounds[axis])):
                bounds[axis] = -1, 1
        
        if dim is not None:
            return bounds[dim]
        else:
            return bounds
    
    @property
    def scene(self):
        """ The root node of the scene viewed by this ViewBox.
        """
        return self._scene

    def add(self, node):
        """ Add an Node to the scene for this ViewBox.

        This is a convenience method equivalent to
        `node.add_parent(viewbox.scene)`

        Parameters
        ----------
        node : instance of Node
            The node to add.
        """
        node.add_parent(self.scene)

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
        * 'fragment' - clipping in the fragment shader
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
        self.update()

    def draw(self, event):
        """ Draw the viewbox border/background

        This also prepares to draw the
        subscene using the configured clipping method.

        Parameters
        ----------
        event : instance of Event
            The draw event.
        """
        # -- Calculate resolution

        # Get current transform and calculate the 'scale' of the viewbox
        size = self.size
        transform = event.visual_to_document
        p0, p1 = transform.map((0, 0)), transform.map(size)
        res = (p1 - p0)[:2]
        res = abs(res[0]), abs(res[1])

        # Set resolution (note that resolution can be non-integer)
        self._resolution = res

        method = self.clip_method
        viewport, fbo = None, None

        if method == 'fragment':
            self._prepare_fragment()
        elif method == 'stencil':
            raise NotImplementedError('No stencil buffer clipping yet.')
        elif method == 'viewport':
            viewport = self._prepare_viewport(event)
        elif method == 'fbo':
            fbo = self._prepare_fbo(event)
        else:
            raise ValueError('Unknown clipping method %s' % method)

        # -- Draw
        super(ViewBox, self).draw(event)

        event.push_viewbox(self)

        # make sure the current drawing system does not attempt to draw
        # the scene.
        event.handled_children.append(self.scene)
        if fbo:
            canvas_transform = event.visual_to_canvas
            offset = canvas_transform.map((0, 0))[:2]
            size = canvas_transform.map(self.size)[:2] - offset

            # Ask the canvas to activate the new FBO
            event.push_fbo(fbo, offset, size)
            event.push_node(self.scene)
            try:
                # Draw subscene to FBO
                self.scene.draw(event)
            finally:
                event.pop_node()
                event.pop_fbo()

            gloo.set_state(cull_face=False)
        elif viewport:
            # Push viewport, draw, pop it
            event.push_viewport(viewport)
            event.push_node(self.scene)
            try:
                self.scene.draw(event)
            finally:
                event.pop_node()
                event.pop_viewport()
        elif method == 'fragment':
            self._clipper.bounds = event.visual_to_framebuffer.map(self.rect)
            event.push_node(self.scene)
            try:
                self.scene.draw(event)
            finally:
                event.pop_node()

        event.pop_viewbox()

    def _prepare_fragment(self, root=None):
        # Todo: should only be run when there are changes in the graph, not
        # on every frame.
        if root is None:
            root = self.scene

        for ch in root.children:
            if isinstance(ch, Visual):
                try:
                    ch.attach(self._clipper)
                except NotImplementedError:
                    # visual does not support clipping
                    pass
            self._prepare_fragment(ch)

    def _prepare_viewport(self, event):
        fb_transform = event.node_transform(map_from=event.node_cs,
                                            map_to=event.framebuffer_cs)
        p1 = fb_transform.map((0, 0))
        p2 = fb_transform.map(self.size)
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
            self._fboprogram = gloo.Program(render_vertex, render_fragment)
            # Create texture
            self._tex = gloo.Texture2D((10, 10, 4), interpolation='linear')
            self._fboprogram['u_texture'] = self._tex
            # Create texcoords and vertices
            # Note y-axis is inverted here because the viewbox coordinate
            # system has origin in the upper-left, but the image is rendered
            # to the framebuffer with origin in the lower-left.
            texcoord = np.array([[0, 1], [1, 1], [0, 0], [1, 0]],
                                dtype=np.float32)
            position = np.zeros((4, 3), np.float32)
            self._fboprogram['a_texcoord'] = gloo.VertexBuffer(texcoord)
            self._fboprogram['a_position'] = self._vert = \
                gloo.VertexBuffer(position)

        # Get fbo, ensure it exists
        fbo = getattr(self, '_fbo', None)
        if True:  # fbo is None:
            self._fbo = 4
            self._fbo = fbo = gloo.FrameBuffer(self._tex,
                                               gloo.RenderBuffer((10, 10)))

        # Set texture coords to make the texture be drawn in the right place
        # Note that we would just use -1..1 if we would use a Visual.
        coords = [[0, 0], [self.size[0], self.size[1]]]
        
        transform = event.get_full_transform()
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
        # todo: use fbo.resize(shape)
        fbo.color_buffer.resize(shape+(4,))
        fbo.depth_buffer.resize(shape)

        return fbo
