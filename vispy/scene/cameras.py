# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
A brief explanation of how cameras work 
---------------------------------------

The view of a camera is determined by its transform (that it has as
being an entity) and its projection. The former is essentially the
position and orientation of the camera, the latter determines field of
view and any non-linear transform (such as perspective).

The projection must return such a transform that the correct view is
mapped onto the size of the viewbox measured in pixels (i.e.
event.resolution).

The subscene actually has a thrird transform, the viewbox_transform,
which is set by the viewbox and which takes care of the mapping from
pixel coordinates to whatever region the viewbox takes in its parent
viewbox.

"""


from __future__ import division

import numpy as np

from . import transforms
from .entity import Entity
from ..util.event import Event
from .transforms import (STTransform, PerspectiveTransform, NullTransform,
                         AffineTransform)


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
        self.events.add(projection_change=Event)
    
    def get_projection(self, event):
        """ Get the projection matrix. Should be overloaded by camera
        classes to define the projection of view.
        """
        # We don't want people to use this base camera
        return NullTransform()

    def scene_mouse_event(self, event):
        """
        This camera's SubScene received a mouse event; update transform 
        accordingly.
        """
        pass


class Fixed2DCamera(Camera):
    """ Camera that presents a 2D view on the world with a given field of 
    view. When the fov is (1, 1) this is the same as a UnitCamera.
    """
    def __init__(self, parent=None, fovx=None, fovy=None):
        Camera.__init__(self, parent)
        if fovx is None:
            fovx = 1, 1
        self.set_fov(fovx, fovy)
    
    def set_fov(self, fovx, fovy=None):
        """ Set the field of view for x and y. Both fovx anf fovy should
        be two-element tuples indicating the range of view. If fovy is not
        given or None, x and y get the same fov.
        """
        # Set x
        fovx = tuple([float(v) for v in fovx])
        assert len(fovx) == 2
        self._fovx = fovx
        # Set y
        if fovy is not None:
            fovy = tuple([float(v) for v in fovy])
            assert len(fovy) == 2
            self._fovy = fovy
        else:
            self._fovy = self._fovx
    
    def get_projection(self, event):
        # Map to the resolution (pixels) available in the viewbox
        fovx, fovy = self._fovx, self._fovy
        w, h = event.resolution
        map_from = (fovx[0], fovy[0]), (fovx[1], fovy[1])
        map_to = (0, h), (w, 0)
        return transforms.STTransform.from_mapping(map_from, map_to)


class TwoDCamera(Camera):

    def __init__(self, parent=None):
        super(TwoDCamera, self).__init__(parent)
        self.transform = STTransform()

    def get_projection(self, event):
        # Our starting point is the range -1..1. Maybe 0..1 makes more sense.
        # Anyway, we should have a way of snapping to the bounds of the visuals
        # that are shown inside our subscene.
        w, h = event.resolution
        map_from = (-1, -1), (1, 1)
        map_to = (0, h), (w, 0)
        return transforms.STTransform.from_mapping(map_from, map_to)
    
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
        self._projection = PerspectiveTransform()
        self.transform = AffineTransform()
        # TODO: allow self.look to be derived from an Anchor
        self._perspective = {
            'look': np.array([0., 0., 0., 1.]),
            'near': 1e-6,
            'far': 1e6,
            'fov': 60,
            'top': np.array([0., 0., 1., 1.]),
            'aspect': 1.0
            }
    
    @property
    def pos(self):
        raise NotImplementedError()
    
    @pos.setter
    def pos(self, pos):
        self.transform.reset()
        self.transform.translate(pos)

    def set_perspective(self, **kwds):
        self._perspective.update(kwds)
        # update camera here
        ar = self._perspective['aspect']
        near = self._perspective['near']
        far = self._perspective['far']
        fov = self._perspective['fov']
        self._projection.set_perspective(fov, ar, near, far)
        self.events.projection_change()

    def _update_transform(self):
        # create transform based on look, near, far, fov, and top.
        self._projection.set_perspective(origin=(0, 0, 0), **self.perspective)

    def get_projection(self):
        return self._projection

    def view_mouse_event(self, event):
        """
        An attached ViewBox received a mouse event;

        """
        pass
