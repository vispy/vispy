# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import numpy as np

from .entity import Entity
from .transforms import STTransform, PerspectiveTransform


class ViewBox(Entity):
    """
    Box class that provides an interactive (pan/zoom) view on its children.    
    """
    def __init__(self, *args, **kwds):
        Entity.__init__(self, *args, **kwds)
        self._child_group = Entity(parents=[self])
        
        # Background color of this viewbox. Used in glClear()
        self._bgcolor = (0.0, 0.0, 0.0, 1.0)
        
        # Each viewbox has a camera. Default is NDCCamera (i.e. null camera)
        self._camera = None
        self.camera = NDCCamera(self)
        
        # Initialize systems
        self._systems = {}
        self._systems['draw'] = DrawingSystem()
    
    @property
    def resolution(self):
        """ The number of pixels (in x and y) that are avalailable in
        the ViewBox.
        
        Note: it would perhaps make sense to call this "size", because
        for the CanvasWithScene, size and resolution are equal by
        definition. However, perhaps we want to give entities a "size"
        property later.
        """
        # todo: ak: in my version I had the transform set to the size.
        # Luke's version seems to asume ND coordinates. I am not sure what
        # is the best one. The root transform is not even used (I think?)
        M = self.transform
        return int(2.0/M.scale[0]), int(2.0/M.scale[1])
    
    @property
    def bgcolor(self):
        """ The background color of the scene. within the viewbox.
        """
        return self._bgcolor
    
    
    @bgcolor.setter
    def bgcolor(self, value):
        # Check / convert
        value = [float(v) for v in value]
        if len(value) < 3:
            raise ValueError('bgcolor must be 3 or 4 floats.')
        elif len(value) == 3:
            value.append(1.0)
        elif len(value) == 4:
            pass
        else:
            raise ValueError('bgcolor must be 3 or 4 floats.')
        # Set
        self._bgcolor = tuple(value)
    
    @property
    def camera(self):
        """ The camera associated with this viewbox. Can be None if there
        are no cameras in the scene.
        """
        return self._camera
    
    @camera.setter
    def camera(self, cam):
        # convenience: set parent if it's an orphan
        if not cam.parents:
            cam.parents = self
        # Test that self is a parent of the camera
        object = cam
        while object is not None:
            # todo: ignoring multi-parentin here, we need Entity.isparent()
            object = object.parents[0]  
            if isinstance(object, ViewBox):
                break
        if object is not self:
            raise ValueError('Given camera is not in the scene of the ViewBox.')
        # Set and (dis)connect events
        if self._camera is not None:
            self._camera.events.update.disconnect(self._camera_update)
        self._camera = cam
        cam.events.update.connect(self._camera_update)
    
    def get_cameras(self):
        """ Get a list of all cameras that live in this scene.
        """
        def getcams(val):
            cams = []
            for entity in val:
                if isinstance(entity, Camera):
                    cams.append(entity)
                if isinstance(entity, ViewBox):
                    pass # Do not go into subscenes
                elif isinstance(entity, Entity):  # if, not elif!
                    cams.extend(getcams(entity))
            return cams
        return getcams(self)
    
    
    def _camera_update(self, event):
        self._child_group.transform = self.camera.transform.inverse()
        
    def add(self, entity):
        entity.add_parent(self._child_group)
    
    def on_mouse_move(self, event):
        if event.handled:
            return
        
        # TODO: original event dispatcher should pick Entities under cursor
        # so we won't need this check.
        if event.press_event is None or not self.rect.contains(*event.press_event.pos[:2]):
            return
            
        self.camera.view_mouse_event(event)

#     def on_paint(self, event):
#         super(ViewBox, self).on_paint(event)
#         
#         r = self.rect.padded(self.margin)
#         r = event.framebuffer_transform.map(r).normalized()
#         event.push_viewport(r.left, r.bottom, r.width, r.height)
#         
#     def on_children_painted(self, event):
#         event.pop_viewport()
    
    def process_system(self, root, system_name):
        """ Process all systems.
        """
        self._systems[system_name].process(self, root)



class Document(Entity):
    """
    Box that represents the area of a rectangular document with 
    physical dimensions. 
    """
    def __init__(self, *args, **kwds):
        self._dpi = 100  # will be used to relate other units to pixels
        super(Document, self).__init__(*args, **kwds)
        
    @property
    def dpi(self):
        return self._dpi
    
    @dpi.setter
    def dpi(self, d):
        self._dpi = dpi
        # TODO: inform tree that resolution has changed..



from .systems import DrawingSystem



from . import transforms  # Needed by cameras


class Camera(Entity):
    """ The Camera class defines the viewpoint from which a scene is
    visualized. It is itself an Entity (with transformations) but by
    default does not draw anything.
    
    Next to the normal transformation, a camera also defines a
    projection tranformation that defines the camera view. This can for
    instance be orthographic, perspective, log, polar, etc.
    """
    
    def __init__(self, parent=None):
        Entity.__init__(self, parent)
        
        # Can be orthograpic, perspective, log, polar, map, etc.
        # Default unit
        self._projection = transforms.NullTransform()
    
    
    def get_projection(self, viewbox):
        """ Get the projection matrix. Should be overloaded by camera
        classes to define the projection of view.
        """
        return self._projection



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
    def get_projection(self, viewbox):
        w, h = viewbox.resolution
        from vispy.util import transforms as trans
        projection = np.eye(4)
        trans.scale(projection, 2.0/w, 2.0/h)
        trans.translate(projection, -1, -1)
        trans.scale(projection, 1, -1)  # Flip y-axis
        return transforms.AffineTransform(projection)



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
            s = 0.97 ** ((p2-p1) * np.array([1, 1]))
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
        super(PerspectiveCamera, self).__init__(parent)
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

