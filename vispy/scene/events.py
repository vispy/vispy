# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..util.event import Event
from .transforms import NullTransform, STTransform, ChainTransform
from ..gloo import gl


class StackItem:
    """ A stack item represents the drawing state for a subscene (a
    scene inside a viewbox).
    """
    def __init__(self, viewbox, resolution):
        # The viewbox and associated camera transform
        self._viewbox = viewbox
        self._camtransform = NullTransform()  # Must be set 
        
        # Path from viewbox to the current entity
        self._path = []
        
        # The resolution (w, h) of the pixel grid provided by the viewbbox
        self._resolution = resolution
        
        # The transform from a parent pixe grid to this one (transform method)
        self._transform_to_viewbox = NullTransform()
        
        # The gl viewport in use for this viewbox (may represent a parent
        # pixel grid if the transform method is used)
        self._viewport = None  # must be set
        
        # A "virtual" viewport inside a real viewport (for transform method)
        self._soft_viewport = 0, 0, 1, 1 # expressed in 0..1 coords
        
        # The fbo in use. If None, it represents the defaulf framebuffer
        self._fbo = None
    
    
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
        
        # Create dummy item that represents the canvas.
        newitem = StackItem(None, canvas.size)
        newitem._viewport = 0, 0, canvas.size[0], canvas.size[1]
        self._stack.append(newitem)
        gl.glViewport(*newitem._viewport)
    
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
        """ Push an entity on the stack. """
        self._stack[-1]._path.append(entity)
    
    def pop_entity(self):
        """ Pop an entity from the stack. """
        self._stack[-1]._path.pop(-1)
    
    # todo: a lot of stuff is rather specific to draw events
    def push_viewbox(self, viewbox, rect, use_transform=False, fbo=None):
        """ Push a viewbox on the stack. This will handle setting
        the viewport, activating fbo, etc.
        """
        
        curitem = None if not self._stack else self._stack[-1]
        newitem = StackItem(viewbox, rect[2:])
        
        assert not (use_transform and fbo)
        set_viewport = not use_transform  # True for 'viewport' and 'fbo' methods
        
        if fbo is not None:
            # Use fbo method
            newitem._fbo = fbo
            fbo.activate()  # is deactivated in pop_viewbox
            newitem._viewport = rect
        
        elif use_transform:
            # Use transform method
            x = curitem._soft_viewport[0] + rect[0]
            y = curitem._soft_viewport[1] + rect[1]
            w, h = rect[2], rect[3]
            # Calculate transform
            res = curitem._viewport[2:]
            transform = STTransform(translate=(2*x/res[0]-0.5, 2*y/res[1]-0.5),
                                    scale=(w/res[0], h/res[1]))
            # Apply
            newitem._soft_viewport = x, y, w, h
            newitem._transform_to_viewbox = transform
            newitem._viewport = curitem._viewport
            newitem._fbo = curitem._fbo
        
        else:
            # Use viewport method
            x = curitem._viewport[0] + rect[0]
            y = curitem._viewport[1] + rect[1]
            # Apply
            newitem._viewport = x, y, rect[2], rect[3]
            newitem._fbo = curitem._fbo
        
        # Apply viewport and add to stack
        if set_viewport:
            gl.glViewport(*newitem._viewport)
            gl.glScissor(*newitem._viewport)
        self._stack.append(newitem)
        
        # Set camera transforms now (newitem must be appended)
        projection = viewbox.camera.get_projection(self)
        camtransform = projection * self._get_camera_transform(viewbox)
        newitem._camtransform = camtransform
        
    
    def pop_viewbox(self):
        """ Pop a viewbox from the stack. This will handle resetting
        viewport, transform, and framebuffer targets.
        """
        olditem = self._stack.pop(-1)
        if self._stack:
            curitem = self._stack[-1]
            # Deal with fbo
            if olditem._fbo is not None:
                olditem._fbo.deactivate()
            if curitem._fbo is not None:
                curitem._fbo.activate()
            # Deal with viewport
            if curitem._viewport != olditem._viewport:
                if curitem._viewport:
                    gl.glViewport(*curitem._viewport)
                    gl.glScissor(*curitem._viewport)
        else:
            pass  # we popped the whole stack!
    
    @property
    def full_transform(self):
        """ The transform that maps from current viewbox to current
        entity; the composition of the line of entities from viewbox to
        here.
        """
        path = self._stack[-1]._path
        tr = [e.parent_transform for e in path[::-1]]
        # TODO: cache transform chains
        return ChainTransform(tr)
    
    
    @property
    def view_transform(self):
        """ The transform from pixel grid to current entity (taking
        camera into account). 
        """
        transform = self._stack[-1]._camtransform * self.full_transform
        transform = transform.simplify()
        # We multiply with NullTransform. This seems needed in some situation.
        # I am not exactly sure, but I suspect that if we don't, different
        # entities can share the transform object, causing problems.
        # todo: look into this              
        transform = transform * NullTransform()
        return transform
    
    
    @property
    def render_transform(self):
        """ The transform that should be used during rendering a visual.
        This may differ from view_transform if the viewbox used the
        'transform' method to provide a pixel grid.
        """
        transform = self._stack[-1]._transform_to_viewbox * self.view_transform
        if isinstance(transform, ChainTransform):
            transform = transform.simplify()
        return transform
    
    
    def _get_camera_transform(self, viewbox):
        """ Calculate the transform from the camera to the viewbox.
        This is the inverse of the transform chain *to* the camera.
        """
        
        # Get total transform of the camera
        object = viewbox.camera
        camtransform = object.transform
        
        while True:
            # todo: does it make sense to have a camera in a multi-path?
            object = object.parents[0]
            if object is viewbox:
                break  # Go until we meet ourselves
            assert isinstance(object, Entity)
            if object.transform is not None:
                camtransform = camtransform * object.transform
        
        # Return inverse!
        return camtransform.inverse()


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
    
    