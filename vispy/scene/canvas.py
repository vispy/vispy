# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..gloo import gl
from .. import app
from .subscene import SubScene
from .transforms import STTransform
from .events import SceneDrawEvent, SceneMouseEvent
from ..util import logger


class SceneCanvas(app.Canvas):
    """ SceneCanvas provides a Canvas that automatically draws the contents
    of a scene.

    """

    def __init__(self, *args, **kwargs):
        self._fb_stack = []  # for storing information about framebuffers in use
        self._vp_stack = []  # for storing information about viewports in use

        app.Canvas.__init__(self, *args, **kwargs)
        self.events.mouse_press.connect(self._process_mouse_event)
        self.events.mouse_move.connect(self._process_mouse_event)
        self.events.mouse_release.connect(self._process_mouse_event)

        self._scene = None
        self.scene = SubScene()

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
        #self._update_document()

    def _scene_update(self, event):
        self.update()

#     def _update_document(self):
#         # 1. Set scaling on document such that its local coordinate system
#         #    represents pixels in the canvas.
#         self.scene.transform.scale = (2. / self.size[0], 2. / self.size[1])
#         self.scene.transform.translate = (-1, -1)
#
#         # 2. Set size of document to match the area of the canvas
#         self.scene.size = (1.0, 1.0)  # root viewbox is in NDC
# AK: no need to set size, we set the size explicitly when drawing.
# actually, we can have a root viewbox that has children, we should not
# touch its transform at all.

    def on_resize(self, event):
        pass
        #self._update_document()
        # Right now viewbox resolution is only available
        # via the event object, which may be sufficient!

    def on_draw(self, event):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        self.push_viewport((0, 0) + self.size)
        
        try:
            if self._scene is None:
                return  # Can happen on initialization
            logger.debug('Canvas draw')
            # Create draw event, which keeps track of the path of transforms
            self._process_entity_count = 0  # for debugging
            scene_event = SceneDrawEvent(canvas=self, event=event)
            self._scene.draw(scene_event)
        finally:
            self.pop_viewport()
        
        if len(self._vp_stack) > 0:
            logger.warn("Viewport stack not fully cleared after draw.")
        if len(self._fb_stack) > 0:
            logger.warn("Framebuffer stack not fully cleared after draw.")

    def _process_mouse_event(self, event):
        scene_event = SceneMouseEvent(canvas=self, event=event)
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
        # Apply
        try:
            self._set_viewport(vp)
        except:
            self._vp_stack.pop()
            raise

    def pop_viewport(self):
        """ Pop a viewport from the stack.
        """
        vp = self._vp_stack.pop()
        # Activate latest
        if len(self._vp_stack) > 0:
            self._set_viewport(self._vp_stack[-1])
        return vp
    
    def _set_viewport(self, vp):
        from .. import gloo
        gloo.set_viewport(*vp)

    def push_fbo(self, fbo, offset, csize):
        """ Push an FBO on the stack, together with the new viewport.
        and the transform to the FBO.
        """
        self._fb_stack.append((fbo, offset, csize))
        
        # Apply
        try:
            fbo.activate()
            h, w = fbo.color_buffer.shape[:2]
            self.push_viewport((0, 0, w, h))
        except:
            self._fb_stack.pop()
            raise
        #from .. import gloo
        #gloo.set_viewport(*viewport)

    def pop_fbo(self):
        """ Pop an FBO from the stack.
        """
        fbo = self._fb_stack.pop()
        fbo[0].deactivate()
        self.pop_viewport()
        if len(self._fb_stack) > 0:
            self._fb_stack[-1].activate()
        return fbo
        ## Pop old
        #ra = self._ra_stack.pop(-1)
        #if ra.fbo is None:
            #raise RuntimeError('FBO stack is empty; cannot pop.')
        #ra.fbo.deactivate()
        ## Activate current
        #ra = self._ra_stack[-1]
        #if ra.fbo:
            #ra.fbo.activate()
        
        #from .. import gloo
        #gl.glViewport(*ra.viewport)
        
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
        # TODO: should this be called px_transform ? 
        #
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
        
        from ..scene.transforms import STTransform
        tr = STTransform()
        tr.set_mapping(map_from, map_to)
        return tr

    @property
    def ndc_transform(self):
        """ The transform that maps from the framebuffer coordinate system to
        normalized device coordinates (which is the obligatory output 
        coordinate system for all vertex shaders). This transform accounts for
        the current glViewport.
        """
        offset, csize, fbsize = self._current_framebuffer()
        x, y, w, h = self._vp_stack[-1]
        
        #map_from = [[0, 0], list(fbsize)]
        #map_to = [[-1, -1], [1, 1]]
        
        ## correct for inverted viewport here.
        #vp = self._vp_stack[-1]
        #if vp[2] < 0:
            #map_to[0][0] = 1
            #map_to[1][0] = -1
        #if vp[3] < 0:
            #map_to[0][1] = 1
            #map_to[1][1] = -1
            
        map_from = [[x, y], [x+w, y+h]]
        map_to = [[-1, -1], [1, 1]]
        
        from ..scene.transforms import STTransform
        tr = STTransform()
        tr.set_mapping(map_from, map_to)
        return tr
    
    @property
    def render_transform(self):
        """ The transform that maps from the Canvas pixel coordinate system 
        <(0, 0) at top-left, (w, h) at bottom-right> to normalized device 
        coordinates within the current glViewport and FBO.

        Most visuals should use this transform when drawing.
        """
        return self.ndc_transform * self.fb_transform
