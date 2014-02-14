# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division
import numpy as np

from ..entity import Entity
from .box import Box
from ...visuals.transforms import STTransform, PerspectiveTransform

class ViewBox(Box):
    """
    Box class that provides an interactive (pan/zoom) view on its children.    
    """
    def __init__(self, *args, **kwds):
        Box.__init__(self, *args, **kwds)
        self._child_group = Entity(parents=[self])
        self._camera = None
        self.camera = TwoDCamera()

    @property
    def camera(self):
        return self._camera
    
    @camera.setter
    def camera(self, cam):
        if self._camera is not None:
            self._camera.events.update.disconnect(self._camera_update)
        self._camera = cam
        cam.events.update.connect(self._camera_update)
        
    def _camera_update(self, event):
        self._child_group.transform = self.camera.transform.inverse()
        
    def add_entity(self, entity):
        entity.add_parent(self._child_group)
    
    def on_mouse_move(self, event):
        if event.handled:
            return
        
        # TODO: original event dispatcher should pick Entities under cursor
        # so we won't need this check.
        if event.press_event is None or not self.rect.contains(*event.press_event.pos[:2]):
            return
            
        self.camera.view_mouse_event(event)

    def on_paint(self, event):
        super(ViewBox, self).on_paint(event)
        
        r = event.framebuffer_transform.map(self.rect)
        event.push_viewport(r.left, r.bottom, r.width, r.height)
        
    def on_children_painted(self, event):
        event.pop_viewport()

class Camera(Entity):
    """ The Camera class defines the viewpoint from which a scene is
    visualized. It is itself an Entity (with transformations) but by
    default does not draw anything.

    By convention, the unit cube in the local coordinate system of the camera
    contains everything that will be visible to a ViewBox using this camera.
    """
    def __init__(self, parent):
        super(Camera, self).__init__(parent)
        
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
        if 1 in event.buttons:
            p1 = np.array(event.last_event.pos)
            p2 = np.array(event.pos)
            self.transform = self.transform * STTransform(translate=p1-p2)
            self.update()
            event.handled = True
        elif 2 in event.buttons:
            p1 = np.array(event.last_event.pos)[:2]
            p2 = np.array(event.pos)[:2]
            s = 0.97 ** ((p2-p1) * np.array([1, -1]))
            center = event.press_event.pos
            # TODO: would be nice if STTransform had a nice scale(s, center) 
            # method like AffineTransform.
            self.transform = (self.transform *
                              STTransform(translate=center) * 
                              STTransform(scale=s) * 
                              STTransform(translate=-center))
            self.update()        
            event.handled = True


class PerspectiveCamera(Camera):
    """
    In progress.
    
    """
    def __init__(self, parent=None):
        super(Camera, self).__init__(parent)
        self.transform = PerspectiveTransform()
        # TODO: allow self.look to be derived from an Anchor
        self._perspective = {
            'look': np.array([0., 0., 0., 1.]),
            'near': 1e-6,
            'far': 1e6,
            'fov': 60,
            'top': np.array([0., 0., 1., 1.])
            }

    def _update_transform(self):
        # create transform based on look, near, far, fov, and top.
        self.transform.set_perspective(origin=(0,0,0), **self.perspective)
        
    def view_mouse_event(self, event):
        """
        An attached ViewBox received a mouse event; 
        
        """
        if 1 in event.buttons:
            p1 = np.array(event.last_event.pos)
            p2 = np.array(event.pos)
            self.transform = self.transform * STTransform(translate=p1-p2)
            self.update()
            event.handled = True
        elif 2 in event.buttons:
            p1 = np.array(event.last_event.pos)[:2]
            p2 = np.array(event.pos)[:2]
            s = 0.97 ** ((p2-p1) * np.array([1, -1]))
            center = event.press_event.pos
            # TODO: would be nice if STTransform had a nice scale(s, center) 
            # method like AffineTransform.
            self.transform = (self.transform *
                              STTransform(translate=center) * 
                              STTransform(scale=s) * 
                              STTransform(translate=-center))
            self.update()        
            event.handled = True

