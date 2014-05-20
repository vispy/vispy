# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..gloo import gl
from .. import app

from .viewbox import Document, ViewBox
from .transforms import STTransform, NullTransform
from .events import ScenePaintEvent, SceneMouseEvent


class SceneCanvas(app.Canvas):
    """ SceneCanvas provides a Canvas that automatically draws the contents
    of a scene.
    
    Automatically constructs a Document instance as the root entity.
    """

    def __init__(self, *args, **kwargs):
        
        app.Canvas.__init__(self, *args, **kwargs)
        self.events.mouse_press.connect(self._process_mouse_event)
        self.events.mouse_move.connect(self._process_mouse_event)
        self.events.mouse_release.connect(self._process_mouse_event)
        
        self._root = None
        #root = Document()
        root = ViewBox()
        root.transform = STTransform()
        self.root = root
        
    @property
    def root(self):
        """ The root entity of the scene graph to be displayed.
        """
        return self._root
    
    @root.setter
    def root(self, e):
        if self._root is not None:
            self._root.events.update.disconnect(self._scene_update)
        self._root = e
        self._root.events.update.connect(self._scene_update)
        self._update_document()

    def _scene_update(self, event):
        self.update()

    def _update_document(self):
        # 1. Set scaling on document such that its local coordinate system 
        #    represents pixels in the canvas.
        self.root.transform.scale = (2. / self.size[0], 2. / self.size[1])
        self.root.transform.translate = (-1, -1)
        
        # 2. Set size of document to match the area of the canvas
        self.root.size = (1.0, 1.0)  # root viewbox is in NDC 

    def on_resize(self, event):
        self._update_document()

    def on_paint(self, event):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        if self._root is None:
            return  # Can happen on initialization
        print('Canvas draw')
        # Create paint event, which keeps track of the path of transforms
        self._process_entity_count = 0  # for debugging
        scene_event = ScenePaintEvent(canvas=self, event=event)
        self._root.paint(scene_event)
        
    
    def _process_mouse_event(self, event):
        scene_event = SceneMouseEvent(canvas=self, event=event)
        # todo: ak: I disabled this for now. I have a feeling that we should also
        # do this via a system
        #self._root._process_mouse_event(scene_event)
        
        # If something in the scene handled the scene_event, then we mark
        # the original event accordingly.
        event.handled = scene_event.handled

    def nd_transform(self):
        """
        Return the transform that maps from ND coordinates to pixel coordinates
        on the Canvas.        
        """
        s = (self.size[0]/2., -self.size[1]/2.)
        t = (self.size[0]/2., self.size[1]/2.)
        return STTransform(scale=s, translate=t)
