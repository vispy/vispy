# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..util.event import Event
from .transforms import NullTransform, STTransform, ChainTransform
from ..gloo import gl


class StackItem:
    def __init__(self, viewbox, resolution):
        self._viewbox = viewbox
        self._resolution = resolution
        self._path = []
        self._transform_to_viewbox = NullTransform()
        self._viewport = None


class SceneEvent(Event):
    """
    SceneEvent is an Event that tracks its path through a scenegraph,
    beginning at a Canvas. It exposes useful information useful during
    drawing. Although the total path can be traced, most properties
    relate to the current viewbox, because entities in general do not
    need to be aware of anything beyond that.
    """
    def __init__(self, type, canvas):
        super(SceneEvent, self).__init__(type=type)
        self._canvas = canvas
        self._stack = []  # list of StackItem objects
        
        # Create dummy item that represents the canvas. This makes that
        # the code in viewbox.paint does not have to care whether it is root.
        self._stack.append(StackItem(None, canvas.size))
    
    @property
    def canvas(self):
        """ The Canvas that originated this SceneEvent
        """
        return self._canvas
    
    @property
    def resolution(self):
        return self._stack[-1]._resolution
    
    @property
    def viewbox(self):
        """ The current viewbox.
        """
        return self._stack[-1]._viewbox
    
    @property
    def path(self):
        """ The path of Entities leading from the latest ViewBox to the
        current recipient of this Event.
        """
        return self._stack[-1]._path
    
    @property
    def total_path(self):
        """ The path of Entities leading from the Canvas to the current recipient
        of this Event.
        """
        # Return flattened path
        total_path = []
        for item in self._stack:
            total_path += item._path
        return total_path

#     def _set_path(self, path):
#         self._path = path
    
    def push_entity(self, entity):
        self._stack[-1]._path.append(entity)
    
    def pop_entity(self):
        self._stack[-1]._path.pop(-1)
    
    # todo: a lot of stuff is rather specific to draw events
    
    def push_viewbox(self, viewbox, resolution, viewport=None, transform=None):
        curitem = None if not self._stack else self._stack[-1]
        newitem = StackItem(viewbox, resolution)
        # Handle viewport
        if viewport is not None:
            newitem._viewport = viewport
            gl.glViewport(*viewport)
        else:
            newitem._viewport = curiem._viewport
        # Handle transform
        if transform is not None:
            # Use a transformation (and the same viewport as parent viewbox)
            #newitem._viewport = curitem._viewport
            transform = self.transform_from_viewbox
            if curitem._transform_to_viewbox:
                transform = curitem._transform_to_viewbox * transform
            newitem._transform_to_viewbox = transform
        
        # Add to stack
        self._stack.append(newitem)
    
    def pop_viewbox(self):
        olditem = self._stack.pop(-1)
        if self._stack:
            curitem = self._stack[-1]
            # Deal with viewport
            if curitem._viewport != olditem._viewport:
                if curitem._viewport:
                    gl.glViewport(*curitem._viewport)
        else:
            pass  # we popped the whole stack!
    
    @property
    def transform_from_viewbox(self):
        """ Return the transform that maps from current viewbox to the recipient
        of this event.
        """
        path = self._stack[-1]._path
        tr = [e.parent_transform for e in path[::-1]]
        # TODO: cache transform chains
        return ChainTransform(tr)
    
    @property
    def transform_to_viewbox(self):
        """ The transfrom from the current viewport to the current viewbox.
        This transform may "pass through" one or more viewboxes.
        """
        return self._stack[-1]._transform_to_viewbox


#     @property
#     def viewport_transform(self):
#         """
#         Return the transform that maps from the end of the path to normalized
#         device coordinates (-1 to 1 within the current glViewport).
#         
#         This transform consists of the root_transform plus a correction for the
#         current glViewport.
#         
#         Most entities should use this transform when painting.
#         """
#         # todo: ak: I am not sure how this works
#         # I suspect it is related to our difference in views on the
#         # role of cameras
#         viewport = self._viewport_stack[-1]
#         csize = self.canvas.size
#         scale = csize[0]/viewport[2], csize[1]/viewport[3]
#         origin = (((csize[0] - 2.0 * viewport[0]) / viewport[2] - 1), 
#                   ((csize[1] - 2.0 * viewport[1]) / viewport[3] - 1))
#         
#         root_tr = self.root_transform
#         return (STTransform(translate=(origin[0], origin[1])) * 
#                 STTransform(scale=scale) * 
#                 root_tr)
        
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
#             tr.append(e.parent_transform)
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

#     def push_viewport(self, x, y, w, h):
#         self._path_stack.append([])
#         self._viewport_stack.append((x, y, w, h))
#         gl.glViewport(int(x), int(y), int(w), int(h))
#         
#     def pop_viewport(self):
#         self._path_stack.pop(-1)
#         self._viewport_stack.pop(-1)
#         gl.glViewport(*map(int, self._viewport_stack[-1]))
        
        
    

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
    
    