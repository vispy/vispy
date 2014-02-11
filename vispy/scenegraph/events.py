# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..util.event import Event
from ..visuals import transforms

class SceneEvent(Event):
    """
    SceneEvent is an Event that tracks its path through a scenegraph, beginning
    at a Canvas.
    """
    def __init__(self, type, canvas):
        super(SceneEvent, self).__init__(type=type)
        self._canvas = canvas
        self._path = []
        
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
        beginning.
        """
        tr = [e.transform for e in self.path[::-1]]
        # TODO: cache transform chains
        return transforms.TransformChain(tr)

    def document_transform(self):
        """
        Return the complete Transform that maps from the end of the path to the 
        first Document in its ancestry.
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
        return transforms.TransformChain(tr)

    def map_to_document(self, obj):
        return self.document_transform().map(obj)
    
    def map_from_document(self, obj):
        return self.document_transform().imap(obj)
    
    def canvas_transform(self):
        """
        Return a Transform that maps from the end of the path to the Canvas.
        """
        tr = [e.transform for e in self.path[::-1]] + [self.canvas.nd_transform()]
        return transforms.TransformChain(tr)
        
    def map_to_canvas(self, obj):
        return self.canvas_transform().map(obj)
    
    def map_from_canvas(self, obj):
        return self.canvas_transform().imap(obj)
    
    
    

class SceneMouseEvent(SceneEvent):
    def __init__(self, event, canvas):
        self.mouse_event = event
        super(SceneMouseEvent, self).__init__(type=event.type, canvas=canvas)

    @property
    def pos(self):
        return self.map_from_canvas(self.mouse_event.pos)

        
class ScenePaintEvent(SceneEvent):
    def __init__(self, event, canvas):
        self.mouse_event = event
        super(ScenePaintEvent, self).__init__(type=event.type, canvas=canvas)
    
    