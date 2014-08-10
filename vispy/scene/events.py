# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..util.event import Event
from .transforms import ChainTransform


class SceneEvent(Event):
    """
    SceneEvent is an Event that tracks its path through a scenegraph,
    beginning at a Canvas. It exposes information useful during drawing
    and user interaction.
    """

    def __init__(self, type, canvas):
        super(SceneEvent, self).__init__(type=type)
        self._canvas = canvas

        # Init stacks
        self._stack = []  # list of entities
        self._viewbox_stack = []

    @property
    def canvas(self):
        """ The Canvas that originated this SceneEvent
        """
        return self._canvas

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
        return self._stack.pop(-1)

    def push_viewbox(self, viewbox):
        self._viewbox_stack.append(viewbox)

    def pop_viewbox(self):
        self._viewbox_stack.pop(-1)

    def push_viewport(self, viewport):
        """ Push a viewport (x, y, w, h) on the stack. It is the
        responsibility of the caller to ensure the given values are
        int. The viewport's origin is defined relative to the current
        viewport.
        """
        self.canvas.push_viewport(viewport)

    def pop_viewport(self):
        """ Pop a viewport from the stack.
        """
        return self.canvas.pop_viewport()

    def push_fbo(self, viewport, fbo, transform):
        """ Push an FBO on the stack, together with the new viewport.
        and the transform to the FBO.
        """
        self.canvas.push_fbo(viewport, fbo, transform)

    def pop_fbo(self):
        """ Pop an FBO from the stack.
        """
        return self.canvas.pop_fbo()
    
    def entity_transform(self, entity):
        """ Return transform that maps from local coordinate system of *entity*
        to the root of the scenegraph.
        """
        # find where entity's ancestry first intersects the current path
        path = []
        while True:
            if entity is None:
                path.insert(0, entity)
                break
            elif entity not in self._stack:
                path.insert(0, entity)
                
                # todo: if this fails, raise a nice exception explaining
                #       the problem.
                entity = entity.parent
            else:
                ind = self._stack.index(entity)
                path = self._stack[:ind+1] + path
                break
        
        tr = [e.transform for e in path]
        # TODO: cache transform chains
        return ChainTransform(tr)
    
    def map_entity_to_doc(self, entity, obj):
        return self.entity_transform(entity).map(obj)
    
    def map_doc_to_entity(self, entity, obj):
        return self.entity_transform(entity).imap(obj)
        
    def map_entity_to_fb(self, entity, obj):
        tr = self.canvas.fb_transform * self.entity_transform(entity)
        return tr.map(obj)
    
    def map_fb_to_entity(self, entity, obj):
        tr = self.canvas.fb_transform * self.entity_transform(entity)
        return tr.imap(obj)
    
    # todo: I think "root_transform" is more descriptive (LC)
    #       or perhaps "scene_transform"
    @property
    def full_transform(self):
        """ The transform that maps from the current entity to the
        top-level entity in the scene.
        """
        tr = [e.transform for e in self._stack]
        # TODO: cache transform chains
        return ChainTransform(tr)

    @property
    def render_transform(self):
        """ The transform that maps from the current entity to
        normalized device coordinates within the current glViewport and
        FBO.

        This transform consists of the full_transform prepended by a
        correction for the current glViewport and/or FBO.

        Most entities should use this transform when drawing.
        """
        #return self.canvas.render_transform * self.full_transform
        return self.full_transform
        #return SceneTransform.get(map_from=self._stack[-1], 
                                  #map_to=self.canvas.ndc,
                                  #path=self._stack])

    @property
    def fb_transform(self):
        """ Transform mapping from the local coordinate system of the current
        entity to the framebuffer coordinate system.
        """
        return self.canvas.fb_transform * self.full_transform
    
    def map_to_fb(self, obj):
        return self.fb_transform.map(obj)

    def map_from_fb(self, obj):
        return self.fb_transform.imap(obj)

    # todo: need to disambiguate this from the doc cs, which is *usually* the
    #       same, but may be separate in some rare situations.
    @property
    def canvas_transform(self):
        """
        Return the transform mapping from the end of the path to Canvas
        pixels (logical pixels).
        
        Canvas_transform is used mainly for mouse interaction. 
        For measuring distance in physical units, the use of document_transform 
        is preferred. 
        """
        return self.full_transform
    
    def map_to_canvas(self, obj):
        """
        Convenience method that maps *obj* from the current coordinate system 
        of the event to the canvas coordinate system (logical pixels; 
        see SceneEvent.canvas_transform).
        """
        return self.canvas_transform.map(obj)
    
    def map_from_canvas(self, obj):
        """
        Convenience method that maps *obj* from the canvas coordinate system 
        (logical pixels; see SceneEvent.canvas_transform) to the current 
        coordinate system of the event.
        """
        return self.canvas_transform.inverse().map(obj)
    

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
        ev = self.copy()
        ev.mouse_event = self.mouse_event.last_event
        return ev

    @property
    def press_event(self):
        if self.mouse_event.press_event is None:
            return None
        ev = self.copy()
        ev.mouse_event = self.mouse_event.press_event
        return ev

    @property
    def button(self):
        return self.mouse_event.button

    @property
    def buttons(self):
        return self.mouse_event.buttons

    @property
    def delta(self):
        return self.mouse_event.delta

    def copy(self):
        ev = self.__class__(self.mouse_event, self._canvas)
        ev._stack = self._stack[:]
        #ev._ra_stack = self._ra_stack[:]
        ev._viewbox_stack = self._viewbox_stack[:]
        return ev


class SceneDrawEvent(SceneEvent):
    def __init__(self, event, canvas):
        self.draw_event = event
        super(SceneDrawEvent, self).__init__(type='draw', canvas=canvas)
