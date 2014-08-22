# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import weakref

from .. import gloo
from .. import app
from .subscene import SubScene
from .entity import Entity
from .transforms import STTransform, TransformCache
from .events import SceneDrawEvent, SceneMouseEvent
from ..color import Color
from ..util import logger


class SceneCanvas(app.Canvas):
    """A Canvas that automatically draws the contents of a scene

    Receives the following events:
    initialize, resize, draw, mouse_press, mouse_release, mouse_move,
    mouse_wheel, key_press, key_release, stylus, touch, close

    Parameters
    ----------
    bgcolor : Color
        The background color to use.

    See also
    --------
    ``app.Canvas`` for other input Parameters.
    """
    def __init__(self, *args, **kwargs):
        self._fb_stack = []  # for storing information about framebuffers used
        self._vp_stack = []  # for storing information about viewports used
        self._scene = None
        self._bgcolor = Color(kwargs.pop('bgcolor', 'black')).rgba

        app.Canvas.__init__(self, *args, **kwargs)
        self.events.mouse_press.connect(self._process_mouse_event)
        self.events.mouse_move.connect(self._process_mouse_event)
        self.events.mouse_release.connect(self._process_mouse_event)
        self.events.mouse_wheel.connect(self._process_mouse_event)

        # Collection of transform caches; one for each root visual used in
        # self.draw_visual(...)
        self._transform_caches = weakref.WeakKeyDictionary()

        # Set up default entity stack: ndc -> fb -> pixels -> scene
        self.ndc = Entity()
        self.framebuffer = Entity(parent=self.ndc)
        self.framebuffer.transform = STTransform()
        self.pixels = Entity(parent=self.framebuffer)
        self.pixels.transform = STTransform()

        self.scene = SubScene(parent=self.pixels)

    @property
    def scene(self):
        """ The SubScene object that represents the root entity of the
        scene graph to be displayed.
        """
        return self._scene

    @scene.setter
    def scene(self, e):
        if self._scene is not None:
            self._scene.events.update.disconnect(self._scene_update)
        self._scene = e
        self._scene.events.update.connect(self._scene_update)

    def _scene_update(self, event):
        self.update()

    def on_draw(self, event):
        gloo.clear(color=self._bgcolor, depth=True)
        if self._scene is None:
            return  # Can happen on initialization
        logger.debug('Canvas draw')
        
        # Draw the scene, but first disconnect its change signal--
        # any changes that take place during the paint should not trigger
        # a subsequent repaint.
        with self.scene.events.update.blocker(self._scene_update):
            self.draw_visual(self.scene)
        
        if len(self._vp_stack) > 0:
            logger.warning("Viewport stack not fully cleared after draw.")
        if len(self._fb_stack) > 0:
            logger.warning("Framebuffer stack not fully cleared after draw.")

    def draw_visual(self, visual, event=None):
        """ Draw a *visual* and its children on the canvas.
        """
        # Create draw event, which keeps track of the path of transforms
        self._process_entity_count = 0  # for debugging
        
        # Get the cache of transforms used for this visual
        tr_cache = self._transform_caches.setdefault(visual, TransformCache())
        # and mark the entire cache as aged
        tr_cache.roll()
        
        scene_event = SceneDrawEvent(canvas=self, event=event, 
                                     transform_cache=tr_cache)
        scene_event.push_viewport((0, 0) + self.size)
        try:
            # Force update of transforms on base entities
            # TODO: this should happen as a reaction to resize, push_viewport,
            #       etc.; not here.  (but note the transforms must change
            #       following push_viewport)
            self.ndc_transform
            self.fb_transform
            
            scene_event.push_entity(self.ndc)
            scene_event.push_entity(self.framebuffer)
            scene_event.push_entity(self.pixels)
            scene_event.push_entity(visual)
            visual.draw(scene_event)
        finally:
            scene_event.pop_viewport()

    def _process_mouse_event(self, event):
        tr_cache = self._transform_caches.setdefault(self.scene, 
                                                     TransformCache())
        scene_event = SceneMouseEvent(canvas=self, event=event,
                                      transform_cache=tr_cache)
        scene_event.push_entity(self.ndc)
        scene_event.push_entity(self.framebuffer)
        scene_event.push_entity(self.pixels)
        scene_event.push_entity(self._scene)
        self._scene._process_mouse_event(scene_event)
        
        # If something in the scene handled the scene_event, then we mark
        # the original event accordingly.
        event.handled = scene_event.handled

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
        self.ndc_transform  # update!
        # Apply
        try:
            self._set_viewport(vp)
        except:
            self._vp_stack.pop()
            self.ndc_transform  # update!
            raise

    def pop_viewport(self):
        """ Pop a viewport from the stack.
        """
        vp = self._vp_stack.pop()
        # Activate latest
        if len(self._vp_stack) > 0:
            self._set_viewport(self._vp_stack[-1])
            self.ndc_transform  # update!
        return vp
    
    def _set_viewport(self, vp):
        from .. import gloo
        gloo.set_viewport(*vp)

    def push_fbo(self, fbo, offset, csize):
        """ Push an FBO on the stack, together with the new viewport.
        and the transform to the FBO.
        """
        self._fb_stack.append((fbo, offset, csize))
        self.fb_transform  # update!
        
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
        self.fb_transform  # update!
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
    def fb_transform(self):
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
            # todo: account for high-res displays here.
            fbsize = csize
        else:
            fbsize = fbo.color_buffer.shape
            # image shape is (rows, cols), unlike canvas shape.
            fbsize = fbsize[1], fbsize[0]  

        map_from = [list(offset), [offset[0] + csize[0], offset[1] + csize[1]]]
        map_to = [[0, fbsize[1]], [fbsize[0], 0]]
        
        self.pixels.transform.set_mapping(map_from, map_to)
        return self.pixels.transform

    @property
    def ndc_transform(self):
        """ The transform that maps from the framebuffer coordinate system to
        normalized device coordinates (which is the obligatory output 
        coordinate system for all vertex shaders). This transform accounts for
        the current glViewport.
        """
        offset, csize, fbsize = self._current_framebuffer()
        x, y, w, h = self._vp_stack[-1]
        
        map_from = [[x, y], [x+w, y+h]]
        map_to = [[-1, -1], [1, 1]]
        
        self.framebuffer.transform.set_mapping(map_from, map_to)
        return self.framebuffer.transform
    
    @property
    def render_transform(self):
        """ The transform that maps from the Canvas pixel coordinate system 
        <(0, 0) at top-left, (w, h) at bottom-right> to normalized device 
        coordinates within the current glViewport and FBO.

        Most visuals should use this transform when drawing.
        """
        return self.ndc_transform * self.fb_transform
