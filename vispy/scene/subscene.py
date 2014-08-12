# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from .entity import Entity
from .systems import DrawingSystem, MouseInputSystem


class SubScene(Entity):
    """ A subscene with entities.

    A subscene can be a child of a Canvas or a ViewBox. It is a
    placeholder for the transform to make the sub scene appear as
    intended. It's transform cannot be mannually set, but its set
    automatically and is based on three components:

      * Viewbox transform: a scale and translation to make the subscene
        be displayed in the boundaries of the viewbox.
      * Projection transform: the camera projection, e.g. perspective
      * position transform: the inverse of the transform from this
        subscene to the camera. This takes care of position and
        orientation of the view.

    TODO: should camera, lights, etc. be properties of the subscene or the
    viewbox? I think of the scene. In that way canvas.scene can simply
    be a subscene.
    """

    def __init__(self, **kwargs):
        Entity.__init__(self, **kwargs)

        # Initialize systems
        self._systems = {}
        self._systems['draw'] = DrawingSystem()
        self._systems['mouse'] = MouseInputSystem()
    
    def draw(self, event):
        # Invoke our drawing system
        self.process_system(event, 'draw') 
    
    def _process_mouse_event(self, event):
        self.process_system(event, 'mouse') 

    def process_system(self, event, system_name):
        """ Process a system.
        """
        self._systems[system_name].process(event, self)
