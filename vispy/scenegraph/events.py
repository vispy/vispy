# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..util.event import Event
from ..visuals import transforms
from ..gloo import gl

class SceneEvent(Event):
    """
    SceneEvent is an Event that tracks its path through a scenegraph, beginning
    at a Canvas.
    """
    def __init__(self, type, canvas):
        super(SceneEvent, self).__init__(type=type)
        self._canvas = canvas
        self._path = []
        self._viewport_stack = []
        
    @property
    def canvas(self):
        """
        The Canvas that originated this SceneEvent
        """
        return self._canvas
    
    @property
    def path(self):
        """
        The path of Entities leading from the Canvas to the current recipient
        of this Event.
        """
        return self._path

    def _set_path(self, path):
        self._path = path
    
    def root_transform(self):
        """
        Return the complete Transform that maps from the end of the path to the
        root.
        """
        tr = [e.transform for e in self.path[::-1]]
        # TODO: cache transform chains
        return transforms.ChainTransform(tr)
    
    def viewport_transform(self):
        """
        Return the transform that maps from the end of the path to normalized
        device coordinates (-1 to 1 within the current glViewport).
        
        This transform consists of the root_transform plus a correction for the
        current glViewport.
        
        Most entities should use this transform when painting.
        """
        root_tr = self.root_transform()
        csize = self.canvas.size
        viewport = self._viewport_stack[-1]
        scale = csize[0]/viewport[2], csize[1]/viewport[3]
        view_tr = (transforms.STTransform(scale=scale) * 
                   transforms.STTransform(translate=(-viewport[0], -viewport[1])))
        return view_tr * root_tr
        
    def framebuffer_transform(self):
        """
        Return the transform mapping from the end of the path to framebuffer
        pixels (device pixels).
        
        This is the coordinate system required by glViewport().
        """
        root_tr = self.root_transform()
        # TODO: How do we get the framebuffer size?
        csize = self.canvas.size
        scale = csize[0]/2.0, -csize[1]/2.0
        fb_tr = (transforms.STTransform(scale=scale) * 
                 transforms.STTransform(translate=(1, -1)))
        return fb_tr * root_tr
        
    def canvas_transform(self):
        """
        Return the transform mapping from the end of the path to Canvas
        pixels (logical pixels).
        
        In most cases, the use of document_transform is preferred over 
        canvas_transform.
        """
        root_tr = self.root_transform()
        csize = self.canvas.size
        scale = csize[0]/2.0, -csize[1]/2.0
        canvas_tr = (transforms.STTransform(scale=scale) * 
                     transforms.STTransform(translate=(1, -1)))
        return canvas_tr * root_tr

    def document_transform(self):
        """
        Return the complete Transform that maps from the end of the path to the 
        first Document in its ancestry.
        
        This coordinate system should be used for all physical unit measurements
        (px, mm, etc.)
        """
        from .entities import Document
        tr = []
        found = False
        for e in self._path[::-1]:
            if isinstance(e, Document):
                found = True
                break
            tr.append(e.transform)
        if not found:
            raise Exception("No Document in the Entity path for this Event.")
        return transforms.ChainTransform(tr)

    def map_to_document(self, obj):
        return self.document_transform().map(obj)
    
    def map_from_document(self, obj):
        return self.document_transform().imap(obj)
    
    def canvas_transform(self):
        """
        Return a Transform that maps from the end of the path to the Canvas.
        """
        tr = [e.transform for e in self.path[::-1]] + [self.canvas.nd_transform()]
        return transforms.ChainTransform(tr)
        
    def map_to_canvas(self, obj):
        return self.canvas_transform().map(obj)
    
    def map_from_canvas(self, obj):
        return self.canvas_transform().imap(obj)
    
    def push_viewport(self, x, y, w, h):
        self._viewport_stack.append((x, y, w, h))
        gl.glViewport(x, y, w, h)
        
    def pop_viewport(self):
        self._viewport_stack.pop()
        gl.glViewport(*self._viewport_stack[-1])
        
        
    

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
        self.mouse_event = event
        super(ScenePaintEvent, self).__init__(type=event.type, canvas=canvas)
    
    