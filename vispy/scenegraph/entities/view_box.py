# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division
import numpy as np

from ..entity import Entity
from .box import Box
from ..visuals.transforms import STTransform

class ViewBox(Box):
    """
    Box class that provides an interactive (pan/zoom) view on its children.    
    """
    def __init__(self, *args, **kwds):
        Box.__init__(self, *args, **kwds)
        self._child_group = Entity(parents=[self])
        self._camera = 
        
    def add_entity(self, entity):
        entity.add_parent(self._child_group)
    
    def on_mouse_move(self, event):
        if event.handled:
            return
        
        # TODO: original event dispatcher should pick Entities under cursor
        # so we won't need this check.
        if not self.rect.contains(*event.pos[:2]):
            return
            
        self.camera.view_mouse_event(event)


class Camera(Entity):
    """ The Camera class defines the viewpoint from which a scene is
    visualized. It is itself an Entity (with transformations) but by
    default does not draw anything.

    By convention, the unit cube in the local coordinate system of the camera
    contains everything that will be visible to a ViewBox using this camera.
    """
    def view_mouse_event(self, event):
        """
        An attached ViewBox received a mouse event; update the camera 
        transform as needed.
        """
        raise NotImplementedError()



class TwoDCamera(Camera):

    def __init__(self, parent=None):
        super(Camera, self).__init__(parent)
        self.transform = STTransform()

    ## xlim and ylim are convenience methods to set the view using limits
    #@property
    #def xlim(self):
        #x = self.transform[-1, 0]
        #dx = self.fov[0] / 2.0
        #return x - dx, x + dx

    #@property
    #def ylim(self):
        #y = self.transform[-1, 1]
        #dy = self.fov[1] / 2.0
        #return y - dy, y + dy

    #@xlim.setter
    #def xlim(self, value):
        #x = 0.5 * (value[0] + value[1])
        #rx = max(value) - min(value)
        #self.fov = rx, self.fov[1]
        #self.transform[-1, 0] = x

    #@ylim.setter
    #def ylim(self, value):
        #y = 0.5 * (value[0] + value[1])
        #ry = max(value) - min(value)
        #self.fov = self.fov[0], ry
        #self.transform[-1, 1] = y

    def view_mouse_event(self, event):
        """
        An attached ViewBox received a mouse event; 
        
        """
        if event.handled:
            return
        
        # TODO: original event dispatcher should pick Entities under cursor
        # so we won't need this check.
        if not self.rect.contains(*event.pos[:2]):
            return
        
        if 1 in event.buttons:
            p1 = np.array(event.last_event.pos)
            p2 = np.array(event.pos)
            self.transform.translate = self.transform.translate + (p1-p2)
            self.update()
            event.handled = True
        elif 2 in event.buttons:
            p1 = np.array(event.last_event.pos)[:2]
            p2 = np.array(event.pos)[:2]
            s = 1.03 ** ((p2-p1) * np.array([1, -1]))
            self._child_group.transform.scale(s, center=event.press_event.pos)
            self.update()        
            event.handled = True
