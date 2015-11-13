# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


from .base_camera import BaseCamera
from ...geometry import Rect


class SyncCamera2D(BaseCamera):
    def __init__(self, sync_x=False, sync_y=False,**kwargs):
        BaseCamera.__init__(self,**kwargs)
        self.sync_x = sync_x
        self.sync_y = sync_y
        
    def set_state(self, state=None, **kwargs):
        D = state or {}
        if 'rect' not in D:
            return 
        for cam in self._linked_cameras:
            r = Rect(D['rect'])
            if cam is self._linked_cameras_no_update:
                continue
            try:
                cam._linked_cameras_no_update = self
                cam_rect = cam.get_state()['rect']
                if not self.sync_x:                                    
                    r.left = cam_rect.left
                    r.right = cam_rect.right
                if not self.sync_y:
                    r.top = cam_rect.top
                    r.bottom = cam_rect.bottom
                cam.set_state({'rect':r})
            finally:
                cam._linked_cameras_no_update = None
