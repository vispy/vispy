# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..util.event import Event
from .transforms import NullTransform, STTransform, ChainTransform
from ..gloo import gl


class RenderArea(object):
    """ Container to store information about the render area, such as
    viewport and information related to the FBO.
    """
    def __init__(self, viewport, size, fbo_transform, fbo=None):
        # The viewport (x, y, w, h)
        self.viewport = viewport
        # Full size of the render area (i.e. resolution)
        self.size = size
        # Transform to get there (for FBO)
        self.fbo_transform = fbo_transform
        # FBO that applies to it. Only necessary for push_fbo
        self.fbo = fbo
        
        # Calculate viewport transform for render_transform
        csize = size
        scale = csize[0]/viewport[2], csize[1]/viewport[3]
        origin = (((csize[0] - 2.0 * viewport[0]) / viewport[2] - 1), 
                  ((csize[1] - 2.0 * viewport[1]) / viewport[3] - 1))
        self.vp_transform = (STTransform(translate=(origin[0], origin[1])) * 
                             STTransform(scale=scale))


class SceneEvent(Event):
    """
    SceneEvent is an Event that tracks its path through a scenegraph,
    beginning at a Canvas. It exposes useful information useful during
    drawing. 
    """
    
    def __init__(self, type, canvas):
        super(SceneEvent, self).__init__(type=type)
        self._canvas = canvas
        
        # Init stacks
        self._stack = []  # list of entities
        self._ra_stack = []  # for viewport & fbo
        self._viewbox_stack = []
        
        # Init render are
        viewport = 0, 0, canvas.size[0], canvas.size[1]
        ra = RenderArea(viewport, canvas.size, NullTransform())
        self._ra_stack.append(ra)
        gl.glViewport(*viewport)
        
        # Init resolution with respect to canvas
        self._resolution = canvas.size  
    
    @property
    def canvas(self):
        """ The Canvas that originated this SceneEvent
        """
        return self._canvas
    
    @property
    def resolution(self):
        return self._resolution

    @property
    def viewbox(self):
        """ The current viewbox.
        """
        if self._viewbox_stack:
            return self._viewbox_stack[-1]
        else: 
            return None
    
    @property
    def path(self):
        """ The path of Entities leading from the root SubScene to the
        current recipient of this Event.
        """
        return self._stack
    
    def push_entity(self, entity):
        """ Push an entity on the stack. """
        self._stack.append(entity)
    
    def pop_entity(self):
        """ Pop an entity from the stack. """
        entity = self._stack.pop(-1)
    
    def push_viewbox(self, viewbox):
        self._viewbox_stack.append(viewbox)
        self._resolution = self._viewbox_stack[-1]._resolution
    
    def pop_viewbox(self):
        self._viewbox_stack.pop(-1)
        if self._viewbox_stack:
            self._resolution = self._viewbox_stack[-1]._resolution
        else:
            self._resolution = self.canvas.size
    
    def push_viewport(self, viewport):
        """ Push a viewport on the stack. It is the responsibility of
        the caller to ensure the given values are int.
        """
        # Append. Take over the transform to the active FBO
        ra = self._ra_stack[-1]
        x, y, w, h = viewport
        viewport = ra.viewport[0] + x, ra.viewport[1] + y, w, h 
        ra_new = RenderArea(viewport, ra.size, ra.fbo_transform)
        self._ra_stack.append(ra_new)
        # Apply
        gl.glViewport(*viewport)
    
    def pop_viewport(self):
        """ Pop a viewport from the stack.
        """
        # Pop old, check
        ra = self._ra_stack.pop(-1)
        if ra.fbo is not None:
            raise RuntimeError('Popping a viewport when top item is an FBO')
        # Activate latest
        ra = self._ra_stack[-1]
        gl.glViewport(*ra.viewport)
    
    def push_fbo(self, viewport, fbo, transform):
        """ Push an FBO on the stack, together with the new viewport.
        and the transform to the FBO.
        """
        # Append, an FBO resets the viewport
        ra_new = RenderArea(viewport, viewport[2:], transform, fbo)
        self._ra_stack.append(ra_new)
        # Apply
        fbo.activate()
        gl.glViewport(*viewport)
    
    def pop_fbo(self):
        """ Pop an FBO from the stack.
        """
        # Pop old
        ra = self._ra_stack.pop(-1)
        if ra.fbo is None:
            raise RuntimeError('Popping an FBO when top item is an viewport')
        ra.fbo.deactivate()
        # Activate current
        ra = self._ra_stack[-1]
        if ra.fbo:
            ra.fbo.activate()
        gl.glViewport(*ra.viewport)
    
    @property
    def full_transform(self):
        """ The transform that maps from the canvas to current
        entity; the composition of the line of entities from viewbox to
        here.
        """
        tr = [e.transform for e in self._stack]
        # TODO: cache transform chains
        return ChainTransform(tr)
    
    @property
    def render_transform(self):
        """ The transform that should be used during rendering a visual.
        Return the transform that maps from the end of the path to normalized
        device coordinates (-1 to 1 within the current glViewport).
        
        This transform consists of the root_transform plus a correction for the
        current glViewport and/or FBO.
        
        Most entities should use this transform when painting.
        """
        if len(self._ra_stack) <= 1:
            return self.full_transform
        else:
            ra = self._ra_stack[-1]
            return ra.fbo_transform * ra.vp_transform * self.full_transform


# AK: we should revive the methods below if and when we need them
#     @property
#     def framebuffer_transform(self):
#         """
#         Return the transform mapping from the end of the path to framebuffer
#         pixels (device pixels).
#         
#         This is the coordinate system required by glViewport().
#         The origin is at the bottom-left corner of the canvas.
#         """
#         root_tr = self.root_transform
#         # TODO: How do we get the framebuffer size?
#         csize = self.canvas.size
#         scale = csize[0]/2.0, csize[1]/2.0
#         fb_tr = (STTransform(scale=scale) * 
#                  STTransform(translate=(1, 1)))
#         return fb_tr * root_tr
        
#     @property
#     def canvas_transform(self):
#         """
#         Return the transform mapping from the end of the path to Canvas
#         pixels (logical pixels).
#         
#         Canvas_transform is used mainly for mouse interaction. 
#         For measuring distance in physical units, the use of document_transform 
#         is preferred. 
#         """
#         root_tr = self.root_transform
#         csize = self.canvas.size
#         scale = csize[0]/2.0, -csize[1]/2.0
#         canvas_tr = (STTransform(scale=scale) * 
#                      STTransform(translate=(1, -1)))
#         return canvas_tr * root_tr
    
#     @property
#     def document_transform(self):
#         """
#         Return the complete Transform that maps from the end of the path to the 
#         first Document in its ancestry.
#         
#         This coordinate system should be used for all physical unit measurements
#         (px, mm, etc.)
#         """
#         from .entities import Document
#         tr = []
#         found = False
#         for e in self._path[::-1]:
#             if isinstance(e, Document):
#                 found = True
#                 break
#             tr.append(e.transform)
#         if not found:
#             raise Exception("No Document in the Entity path for this Event.")
#         return ChainTransform(tr)

#     def map_to_document(self, obj):
#         return self.document_transform.map(obj)
#     
#     def map_from_document(self, obj):
#         return self.document_transform.imap(obj)
    
#     def map_to_canvas(self, obj):
#         return self.canvas_transform.map(obj)
#     
#     def map_from_canvas(self, obj):
#         return self.canvas_transform.imap(obj)


        
        
    

class SceneMouseEvent(SceneEvent):
    def __init__(self, event, canvas):
        self.mouse_event = event
        super(SceneMouseEvent, self).__init__(type=event.type, canvas=canvas)

    @property
    def pos(self):
        return self.map_from_canvas(self.mouse_event.pos)

    @property
    def last_event(self):
        if self.mouse_event.last_event is None:
            return None
        ev = SceneMouseEvent(self.mouse_event.last_event, self.canvas)
        ev._set_path(self.path)
        return ev
        
    @property
    def press_event(self):
        if self.mouse_event.press_event is None:
            return None
        ev = SceneMouseEvent(self.mouse_event.press_event, self.canvas)
        ev._set_path(self.path)
        return ev
        
    @property
    def button(self):
        return self.mouse_event.button
        
    @property
    def buttons(self):
        return self.mouse_event.buttons
        
class ScenePaintEvent(SceneEvent):
    def __init__(self, event, canvas):
        self.paint_event = event
        super(ScenePaintEvent, self).__init__(type=event.type, canvas=canvas)
    
    