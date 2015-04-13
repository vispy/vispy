# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import weakref

from .. import gloo
from .. import app
from .node import Node
from ..visuals.transforms import STTransform, TransformCache
from ..color import Color
from ..util import logger
from ..util.profiler import Profiler
from .subscene import SubScene
from .events import SceneDrawEvent, SceneMouseEvent
from .widgets import Widget


class SceneCanvas(app.Canvas):
    """ SceneCanvas provides a Canvas that automatically draws the contents
    of a scene.

    Receives the following events:
    initialize, resize, draw, mouse_press, mouse_release, mouse_move,
    mouse_wheel, key_press, key_release, stylus, touch, close

    Parameters
    ----------
    title : str
        The widget title
    size : (width, height)
        The size of the window.
    position : (x, y)
        The position of the window in screen coordinates.
    show : bool
        Whether to show the widget immediately. Default False.
    autoswap : bool
        Whether to swap the buffers automatically after a draw event.
        Default True. If True, the ``swap_buffers`` Canvas method will
        be called last (by default) by the ``canvas.draw`` event handler.
    app : Application | str
        Give vispy Application instance to use as a backend.
        (vispy.app is used by default.) If str, then an application
        using the chosen backend (e.g., 'pyglet') will be created.
        Note the canvas application can be accessed at ``canvas.app``.
    create_native : bool
        Whether to create the widget immediately. Default True.
    init_gloo : bool
        Initialize standard values in gloo (e.g., ``GL_POINT_SPRITE``).
    vsync : bool
        Enable vertical synchronization.
    resizable : bool
        Allow the window to be resized.
    decorate : bool
        Decorate the window.
    fullscreen : bool | int
        If False, windowed mode is used (default). If True, the default
        monitor is used. If int, the given monitor number is used.
    context : dict | instance SharedContext | None
        OpenGL configuration to use when creating the context for the
        canvas, or a context to share objects with. If None,
        ``vispy.gloo.get_default_config`` will be used to set the OpenGL
        context parameters. Alternatively, the ``canvas.context``
        property from an existing canvas (using the same backend) can
        be used, thereby sharing objects between contexts.
    keys : str | dict | None
        Default key mapping to use. If 'interactive', escape and F11 will
        close the canvas and toggle full-screen mode, respectively.
        If dict, maps keys to functions. If dict values are strings,
        they are assumed to be ``Canvas`` methods, otherwise they should
        be callable.
    parent : widget-object
        The parent widget if this makes sense for the used backend.
    dpi : float | None
        Resolution in dots-per-inch to use for the canvas. If dpi is None,
        then the value will be determined by querying the global config first,
        and then the operating system.
    bgcolor : Color
        The background color to use.

    See also
    --------
    vispy.app.Canvas
    """
    def __init__(self, *args, **kwargs):
        self._fb_stack = []  # for storing information about framebuffers used
        self._vp_stack = []  # for storing information about viewports used
        self._scene = None
        
        # A default widget that follows the shape of the canvas
        self._central_widget = None

        self._bgcolor = Color(kwargs.pop('bgcolor', 'black')).rgba

        app.Canvas.__init__(self, *args, **kwargs)
        self.events.mouse_press.connect(self._process_mouse_event)
        self.events.mouse_move.connect(self._process_mouse_event)
        self.events.mouse_release.connect(self._process_mouse_event)
        self.events.mouse_wheel.connect(self._process_mouse_event)

        # Collection of transform caches; one for each root visual used in 
        # self.draw_visual(...)
        self._transform_caches = weakref.WeakKeyDictionary()

        # Set up default node stack: ndc -> fb -> canvas -> scene
        self.render_cs = Node(name="render_cs")
        self.framebuffer_cs = Node(parent=self.render_cs, 
                                   name="framebuffer_cs")
        self.framebuffer_cs.transform = STTransform()
        self.canvas_cs = Node(parent=self.framebuffer_cs,
                              name="canvas_cs")
        self.canvas_cs.transform = STTransform()
        # By default, the document coordinate system is the canvas.
        self.canvas_cs.document = self.canvas_cs
        
        self.scene = SubScene(parent=self.canvas_cs)
        
    @property
    def scene(self):
        """ The SubScene object that represents the root node of the
        scene graph to be displayed.
        """
        return self._scene

    @scene.setter
    def scene(self, e):
        if self._scene is not None:
            self._scene.events.update.disconnect(self._scene_update)
        self._scene = e
        self._scene.events.update.connect(self._scene_update)

    @property
    def central_widget(self):
        """ Returns the default widget that occupies the entire area of the
        canvas. 
        """
        if self._central_widget is None:
            self._central_widget = Widget(size=self.size, parent=self.scene)
        return self._central_widget

    def _scene_update(self, event):
        self.update()

    def on_draw(self, event):
        if self._scene is None:
            return  # Can happen on initialization
        logger.debug('Canvas draw')

        self._draw_scene()

    def render(self, region=None, size=None):
        """ Render the scene to an offscreen buffer and return the image array.
        
        Parameters
        ----------
        region : tuple | None
            Specifies the region of the canvas to render. Format is 
            (x, y, w, h). By default, the entire canvas is rendered.
        size : tuple | None
            Specifies the size of the image array to return. If no size is 
            given, then the size of the *region* is used. This argument allows
            the scene to be rendered at resolutions different from the native
            canvas resolution.

        Returns
        -------
        image : array
            Numpy array of type ubyte and shape (h, w, 4). Index [0, 0] is the 
            upper-left corner of the rendered region.
        
        """
        # Set up a framebuffer to render to
        offset = (0, 0) if region is None else region[:2]
        csize = self.size if region is None else region[2:]
        size = csize if size is None else size
        fbo = gloo.FrameBuffer(color=gloo.RenderBuffer(size[::-1]),
                               depth=gloo.RenderBuffer(size[::-1]))

        self.push_fbo(fbo, offset, csize)
        try:
            self._draw_scene(viewport=(0, 0) + size)
            return fbo.read()
        finally:
            self.pop_fbo()

    def _draw_scene(self, viewport=None):
        self.context.clear(color=self._bgcolor, depth=True)
        # Draw the scene, but first disconnect its change signal--
        # any changes that take place during the paint should not trigger
        # a subsequent repaint.
        with self.scene.events.update.blocker(self._scene_update):
            self.draw_visual(self.scene, viewport=viewport)

    def draw_visual(self, visual, event=None, viewport=None):
        """ Draw a visual to the canvas or currently active framebuffer.
        
        Parameters
        ----------
        visual : Visual
            The visual to draw
        event : None or DrawEvent
            Optionally specifies the original canvas draw event that initiated
            this draw.
        viewport : tuple | None
            Optionally specifies the viewport to use. If None, the entire
            physical size is used.
        """
        prof = Profiler()
        nfb = len(self._fb_stack)
        nvp = len(self._vp_stack)
        
        # Create draw event, which keeps track of the path of transforms
        self._process_node_count = 0  # for debugging
        
        # Get the cache of transforms used for this visual
        tr_cache = self._transform_caches.setdefault(visual, TransformCache())
        # and mark the entire cache as aged
        tr_cache.roll()
        prof('roll transform cache')
        
        scene_event = SceneDrawEvent(canvas=self, event=event, 
                                     transform_cache=tr_cache)
        prof('create SceneDrawEvent')
        
        vp = (0, 0) + self.physical_size if viewport is None else viewport
        scene_event.push_viewport(vp)
        prof('push_viewport')
        try:
            # Force update of transforms on base entities
            # TODO: this should happen as a reaction to resize, push_viewport,
            #       etc.; not here.  (but note the transforms must change
            #       following push_viewport)
            self.fb_ndc_transform
            self.canvas_fb_transform
            
            scene_event.push_node(self.render_cs)
            scene_event.push_node(self.framebuffer_cs)
            scene_event.push_node(self.canvas_cs)
            scene_event.push_node(visual)
            prof('initialize event scenegraph')
            visual.draw(scene_event)
            prof('draw scene')
        finally:
            scene_event.pop_viewport()

        if len(self._vp_stack) > nvp:
            logger.warning("Viewport stack not fully cleared after draw.")
        if len(self._fb_stack) > nfb:
            logger.warning("Framebuffer stack not fully cleared after draw.")

    def _process_mouse_event(self, event):
        prof = Profiler()
        tr_cache = self._transform_caches.setdefault(self.scene, 
                                                     TransformCache())
        scene_event = SceneMouseEvent(canvas=self, event=event,
                                      transform_cache=tr_cache)
        scene_event.push_node(self.render_cs)
        scene_event.push_node(self.framebuffer_cs)
        scene_event.push_node(self.canvas_cs)
        scene_event.push_node(self._scene)
        prof('prepare mouse event')
        
        self._scene._process_mouse_event(scene_event)
        prof('process')
        
        # If something in the scene handled the scene_event, then we mark
        # the original event accordingly.
        event.handled = scene_event.handled

    def on_resize(self, event):
        if self._central_widget is not None:
            self._central_widget.size = self.size

    # -------------------------------------------------- transform handling ---
    def push_viewport(self, viewport):
        """ Push a viewport (x, y, w, h) on the stack. It is the
        responsibility of the caller to ensure the given values are
        int. The viewport's origin is defined relative to the current
        viewport.
        """
        vp = list(viewport)
        # Normalize viewport before setting;
        if vp[2] < 0:
            vp[0] += vp[2]
            vp[2] *= -1
        if vp[3] < 0:
            vp[1] += vp[3]
            vp[3] *= -1
            
        self._vp_stack.append(vp)
        self.fb_ndc_transform  # update!
        # Apply
        try:
            self._set_viewport(vp)
        except:
            self._vp_stack.pop()
            self.fb_ndc_transform  # update!
            raise

    def pop_viewport(self):
        """ Pop a viewport from the stack.
        """
        vp = self._vp_stack.pop()
        # Activate latest
        if len(self._vp_stack) > 0:
            self._set_viewport(self._vp_stack[-1])
            self.fb_ndc_transform  # update!
        return vp
    
    def _set_viewport(self, vp):
        self.context.set_viewport(*vp)

    def push_fbo(self, fbo, offset, csize):
        """ Push an FBO on the stack, together with the new viewport.
        and the transform to the FBO.
        """
        self._fb_stack.append((fbo, offset, csize))
        self.canvas_fb_transform  # update!
        
        # Apply
        try:
            fbo.activate()
            h, w = fbo.color_buffer.shape[:2]
            self.push_viewport((0, 0, w, h))
        except Exception:
            self._fb_stack.pop()
            raise

    def pop_fbo(self):
        """ Pop an FBO from the stack.
        """
        fbo = self._fb_stack.pop()
        fbo[0].deactivate()
        self.pop_viewport()
        if len(self._fb_stack) > 0:
            old_fbo = self._fb_stack[-1]
            old_fbo[0].activate()
        self.canvas_fb_transform  # update!
        return fbo
        
    def _current_framebuffer(self):
        """ Return (fbo, origin, canvas_size) for the current
        FBO on the stack, or for the canvas if there is no FBO.
        """
        if len(self._fb_stack) == 0:
            return None, (0, 0), self.size
        else:
            return self._fb_stack[-1]

    @property
    def canvas_fb_transform(self):
        """ The transform that maps from the canvas coordinate system to the
        current framebuffer coordinate system. 
        
        The framebuffer coordinate 
        system is used for antialiasing calculations, and is also the 
        system used when specifying coordinates for glViewport 
        (or gloo.set_viewport). Its origin is in the lower-left corner (as
        opposed to the document / canvas coordinate system, which has its
        origin in the upper-left corner).
        
        Often the canvas and framebuffer coordinate systems are identical. 
        However, some systems with high-resolution 
        displays may use framebuffers with higher resolution than the reported
        size of the canvas. Likewise, when rendering to an FBO, the resolution
        and offset of the framebuffer may not match the canvas. 
        """
        fbo, offset, csize = self._current_framebuffer()
        if fbo is None:
            fbsize = self.physical_size
        else:
            fbsize = fbo.color_buffer.shape
            # image shape is (rows, cols), unlike canvas shape.
            fbsize = fbsize[1], fbsize[0]  

        map_from = [list(offset), [offset[0] + csize[0], offset[1] + csize[1]]]
        map_to = [[0, fbsize[1]], [fbsize[0], 0]]
        
        self.canvas_cs.transform.set_mapping(map_from, map_to)
        return self.canvas_cs.transform

    @property
    def fb_ndc_transform(self):
        """ The transform that maps from the framebuffer coordinate system to
        normalized device coordinates (which is the obligatory output 
        coordinate system for all vertex shaders). This transform accounts for
        the current glViewport.
        """
        offset, csize, fbsize = self._current_framebuffer()
        x, y, w, h = self._vp_stack[-1]
        
        map_from = [[x, y], [x+w, y+h]]
        map_to = [[-1, -1], [1, 1]]
        
        self.framebuffer_cs.transform.set_mapping(map_from, map_to)
        return self.framebuffer_cs.transform
    
    @property
    def render_transform(self):
        """ The transform that maps from the Canvas pixel coordinate system 
        <(0, 0) at top-left, (w, h) at bottom-right> to normalized device 
        coordinates within the current glViewport and FBO.

        Most visuals should use this transform when drawing.
        """
        return self.fb_ndc_transform * self.canvas_fb_transform

    @property
    def bgcolor(self):
        return Color(self._bgcolor)

    @bgcolor.setter
    def bgcolor(self, color):
        self._bgcolor = Color(color).rgba
        if hasattr(self, '_backend'):
            self.update()
