# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from . import transforms
from .entity import Entity
from .transforms import STTransform, PerspectiveTransform


class Camera(Entity):
    """ The Camera class defines the viewpoint from which a scene is
    visualized. It is itself an Entity (with transformations) but by
    default does not draw anything.

    Next to the normal transformation, a camera also defines a
    projection transformation that defines the camera view. This can for
    instance be orthographic, perspective, log, polar, etc.
    
    Cameras are also responsible for handling any user input that
    should affect the viewpoint of projection of the camera.
    """

    def __init__(self, parent=None):
        Entity.__init__(self, parent)

        # Can be orthograpic, perspective, log, polar, map, etc.
        # Default unit
        self._projection = transforms.NullTransform()

    def get_projection(self, event):
        """ Get the projection matrix. Should be overloaded by camera
        classes to define the projection of view.
        """
        return self._projection

    def scene_mouse_event(self, event):
        """
        This camera's SubScene received a mouse event; update transform 
        accordingly.
        """
        pass


class NDCCamera(Camera):
    """ Camera that presents a view on the world in normalized device
    coordinates (-1..1).
    """
    pass


class PixelCamera(Camera):
    """ Camera that presents a view on the world in pixel coordinates.
    The coordinates map directly to the viewbox coordinates. The origin
    is in the upper left.
    """
    def get_projection(self, event):
        # find bounds of our viewbox relative to the document coordinate system
        vb = event.viewbox
        corners = np.array([[0, 0], list(vb.size)])
        mapped = event.map_entity_to_doc(vb, corners)[:, :2]
        
        # size of viewbox relative to doc cs
        mapped_size = abs(mapped[1] - mapped[0])
        
        # corners of visible coordinate system in scene
        scene_corners = np.array([[0, 0], mapped_size])
        ul = scene_corners.min(axis=0)
        br = scene_corners.max(axis=0)
        
        # return transform that maps viewbox bounds to unit box
        trans = transforms.STTransform()
        trans.set_mapping([ul, br], [[-1, 1], [1, -1]])
        return trans


class TwoDCamera(Camera):

    def __init__(self, parent=None):
        super(TwoDCamera, self).__init__(parent)
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

    def scene_mouse_event(self, event):
        """
        This camera's SubScene received a mouse event; update transform 
        accordingly.
        """
        
        if 1 in event.buttons:
            p1 = np.array(event.last_event.pos)[:2]
            p2 = np.array(event.pos)[:2]
            #p1 = event.map_to_canvas(p1)
            #p2 = event.map_to_canvas(p2)
            self.transform = STTransform(translate=p1-p2) * self.transform
            self.update()
            event.handled = True
        elif 2 in event.buttons:
            p1 = np.array(event.last_event.pos)[:2]
            p2 = np.array(event.pos)[:2]
            p1c = event.map_to_canvas(p1)[:2]
            p2c = event.map_to_canvas(p2)[:2]
            s = 0.97 ** ((p2c-p1c) * np.array([1, -1]))
            center = event.press_event.pos[:2]
            #center[0] -= 1
            #center[1] = (center[1] * 2) - 1
            # TODO: would be nice if STTransform had a nice scale(s, center) 
            # method like AffineTransform.
            self.transform = (STTransform(translate=center) * 
                              STTransform(scale=s) * 
                              STTransform(translate=-center) *
                              self.transform)
            self.update()        
            event.handled = True


class PerspectiveCamera(Camera):
    """
    In progress.

    """
    def __init__(self, parent=None):
        super(PerspectiveCamera, self).__init__(parent)
        self.transform = PerspectiveTransform()
        # TODO: allow self.look to be derived from an Anchor
        self._perspective = {
            'look': np.array([0., 0., 0., 1.]),
            'near': 1e-6,
            'far': 1e6,
            'fov': 60,
            'top': np.array([0., 0., 1., 1.])}

    def _update_transform(self):
        # create transform based on look, near, far, fov, and top.
        self.transform.set_perspective(origin=(0, 0, 0), **self.perspective)

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
