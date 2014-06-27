# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from .entity import Entity
from .cameras import Camera, NDCCamera
from .transforms import NullTransform
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

    def __init__(self, parent=None):
        Entity.__init__(self, parent)

        # Each scene has a camera. Default is NDCCamera (i.e. null camera)
        self._camera = None
        self.camera = NDCCamera(self)

        self.viewbox_transform = NullTransform()

        # Initialize systems
        self._systems = {}
        self._systems['draw'] = DrawingSystem()
        self._systems['mouse'] = MouseInputSystem()
    
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
            # todo: ignoring multi-parenting here, we need Entity.isparent()
            object = object.parents[0]
            if isinstance(object, SubScene):
                break
        if object is not self:
            raise ValueError('Given camera is not in the scene itself.')
        # Set and (dis)connect events
#         if self._camera is not None:
#             self._camera.events.update.disconnect(self._camera_update)
        self._camera = cam
#         cam.events.update.connect(self._camera_update)

    def get_cameras(self):
        """ Get a list of all cameras that live in this scene.
        """
        def getcams(val):
            cams = []
            for entity in val:
                if isinstance(entity, Camera):
                    cams.append(entity)
                if isinstance(entity, SubScene):
                    pass  # Do not go into subscenes
                elif isinstance(entity, Entity):  # if, not elif!
                    cams.extend(getcams(entity))
            return cams
        return getcams(self)
    
    @property
    def transform(self):
        return self._transform
    
    @transform.setter
    def transform(self, transform):
        raise RuntimeError('Cannot set transform of SubScene object.')
    
    def _update_transform(self, event):
        # Get three components of the transform
        viewbox = self.viewbox_transform
        projection = self.camera.get_projection(event)
        position = self._get_camera_transform()
        # Combine and set
        self._transform = viewbox * projection * position

    def _get_camera_transform(self):
        """ Calculate the transform from the camera to the SubScene entity.
        This transform maps from scene coordinates to the local coordinate
        system of the camera.
        """
        return self.entity_transform(self.camera).inverse()
    
    def draw(self, event):
        # todo: update transform only when necessay
        self._update_transform(event)

        # Invoke our drawing system
        self.process_system(event, 'draw') 
    
    def _process_mouse_event(self, event):
        self.process_system(event, 'mouse') 

    def process_system(self, event, system_name):
        """ Process a system.
        """
        self._systems[system_name].process(event, self)

    def on_mouse_move(self, event):
        if event.press_event is None or event.handled:
            return
        
        # Let camera handle mouse interaction
        self.camera.scene_mouse_event(event)
