# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
from __future__ import division

import numpy as np

from .cameras import PanZoomCamera
from ...visuals.transforms.nonlinear import (MagnifyTransform, 
                                             Magnify1DTransform)
from ...app import Timer


class MagnifyCamera(PanZoomCamera):
    """ Camera implementing a MagnifyTransform combined with PanZoomCamera.
    
    This Camera uses the mouse cursor position to set the center position of
    the MagnifyTransform, and uses mouse wheel events to adjust the 
    magnification factor.
    
    At high magnification, very small mouse movements can result in large
    changes, so we use a timer to animate transitions in the transform 
    properties.
    
    The camera also adjusts the size of its "lens" area when the view is
    resized.
    """
    transform_class = MagnifyTransform
    
    def __init__(self, size_factor=0.25, radius_ratio=0.9, **kwds):
        # what fraction of the view width to use for radius
        self.size_factor = size_factor
        
        # ratio of inner to outer lens radius
        self.radius_ratio = radius_ratio
        
        # Extract kwargs for panzoom
        camkwargs = {}
        for key in ('parent', 'name'):
            if key in kwds:
                camkwargs[key] = kwds.pop(key)
        
        # Create the mag transform - kwrds go here
        self.mag = self.transform_class(**kwds)
        
        # for handling smooth transitions
        self.mag_target = self.mag.mag
        self.mag._mag = self.mag_target
        self.mouse_pos = None
        self.timer = Timer(interval=0.016, connect=self.on_timer)
        
        super(MagnifyCamera, self).__init__(**camkwargs)

        # This tells the camera to insert the magnification transform at the
        # beginning of the transform it applies to the scene. This is the 
        # correct place for the mag transform because:
        # 1. We want it to apply to everything inside the scene, and not to
        #    the ViewBox itself or anything outside of the ViewBox.
        # 2. We do _not_ want the pan/zoom transforms applied first, because
        #    the scale factors implemented there should not change the shape
        #    of the lens.
        self.pre_transform = self.mag
        
    def view_mouse_event(self, event):
        # When the attached ViewBox reseives a mouse event, it is sent to the
        # camera here.
        
        self.mouse_pos = event.pos[:2]
        if event.type == 'mouse_wheel':
            # wheel rolled; adjust the magnification factor and hide the 
            # event from the superclass
            m = self.mag_target 
            m *= 1.2 ** event.delta[1]
            m = m if m > 1 else 1
            self.mag_target = m
        else:
            # send everything _except_ wheel events to the superclass
            super(MagnifyCamera, self).view_mouse_event(event)
            
        # start the timer to smoothly modify the transform properties. 
        if not self.timer.running:
            self.timer.start()
        
        self._update_transform()
    
    def on_timer(self, event=None):
        # Smoothly update center and magnification properties of the transform
        k = np.clip(100. / self.mag.mag, 10, 100)
        s = 10**(-k * event.dt)
            
        c = np.array(self.mag.center)
        c1 = c * s + self.mouse_pos * (1-s)
        
        m = self.mag.mag * s + self.mag_target * (1-s)
        
        # If changes are very small, then it is safe to stop the timer.
        if (np.all(np.abs((c - c1) / c1) < 1e-5) and 
                (np.abs(np.log(m / self.mag.mag)) < 1e-3)):
            self.timer.stop()
            
        self.mag.center = c1
        self.mag.mag = m
            
        self._update_transform()

    def view_resize_event(self, event):
        # when the view resizes, we change the lens radii to match.
        vbs = self.viewbox.size
        r = min(vbs) * self.size_factor
        self.mag.radii = r * self.radius_ratio, r
        self._update_transform()

    def view_changed(self):
        # make sure radii are updated when a view is attached.
        self.view_resize_event(None)


class Magnify1DCamera(MagnifyCamera):
    transform_class = Magnify1DTransform
