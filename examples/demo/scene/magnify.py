# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Demonstrates use of custom Camera subclasses combined with MagnifyTransform
to implement a (flashy) data-exploration tool.

Here we use MagnifyTransform to allow the user to zoom in on a particular 
region of data, while also keeping the entire data set visible for reference.
The custom camera classes are responsible for inserting MagnifyTransform
at the transform of each viewbox scene, while also updating those transforms
to respond to user input.
"""

import numpy as np
import vispy.scene
from vispy import app
from vispy.scene import visuals
from vispy.scene.transforms.nonlinear import (MagnifyTransform, 
                                              Magnify1DTransform)
from vispy.scene.transforms import STTransform
from vispy.util import filter 


class MagCamera(vispy.scene.cameras.PanZoomCamera):
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
        
        # Create the mag transform
        self.mag = self.transform_class(**kwds)
        
        # for handling smooth transitions
        self.mag_target = self.mag.mag
        self.mag._mag = self.mag_target
        self.mouse_pos = None
        self.timer = app.Timer(interval=0.016, connect=self.on_timer)
        
        super(MagCamera, self).__init__()

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
            super(MagCamera, self).view_mouse_event(event)
            
        # start the timer to smoothly modify the transform properties. 
        self.timer.start()
        
        self._update_transform()
    
    def on_timer(self, event=None):
        # Smoothly update center and magnification properties of the transform
        s = 0.0001**event.dt
            
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
    
    #def _set_scene_transform(self, tr):
        #super(MagCamera, self)._set_scene_transform(self.mag * tr)


class Mag1DCamera(MagCamera):
    transform_class = Magnify1DTransform


# 
# Make a canvas and partition it into 3 viewboxes.
#
canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
grid = canvas.central_widget.add_grid()

vb1 = grid.add_view(row=0, col=0, col_span=2)
vb2 = grid.add_view(row=1, col=0)
vb3 = grid.add_view(row=1, col=1)

#
# Top viewbox: Show a plot line containing fine structure with a 1D 
# magnigication transform.
#
vb1.camera = Mag1DCamera(mag=4, size_factor=0.6, radius_ratio=0.8)
vb1.camera.rect = 0, 30, 100000, 100

pos = np.empty((100000, 2))
pos[:, 0] = np.arange(100000)
pos[:, 1] = np.random.normal(size=100000, loc=50, scale=10)
pos[:, 1] = filter.gaussian_filter(pos[:, 1], 20)
pos[:, 1] += np.random.normal(size=100000, loc=0, scale=2)
pos[:, 1][pos[:, 1] > 55] += 100
pos[:, 1] = filter.gaussian_filter(pos[:, 1], 2)
line = visuals.Line(pos, color='white', parent=vb1.scene)
line.transform = STTransform(translate=(0, 0, -0.1))

grid1 = visuals.GridLines(parent=vb1.scene)


#
# Bottom-left viewbox: Image with circular magnification lens.
#
size = (100, 100)
vb2.camera = MagCamera(mag=3, size_factor=0.3, radius_ratio=0.6)
vb2.camera.rect = (-10, -10, size[0]+20, size[1]+20) 

img_data = np.random.normal(size=size+(3,), loc=58, scale=20).astype(np.ubyte)
image = visuals.Image(img_data, method='impostor', parent=vb2.scene)


#
# Bottom-right viewbox: Scatter plot with many clusters of varying scale.
#
vb3.camera = MagCamera(mag=3, size_factor=0.3, radius_ratio=0.9)
vb3.camera.rect = (-5, -5, 10, 10)

centers = np.random.normal(size=(50, 2))
pos = np.random.normal(size=(100000, 2), scale=0.2)
indexes = np.random.normal(size=100000, loc=centers.shape[0]/2., 
                           scale=centers.shape[0]/3.)
indexes = np.clip(indexes, 0, centers.shape[0]-1).astype(int)
scales = np.log10(np.linspace(-2, 1, centers.shape[0]))[indexes][:, np.newaxis]
pos *= scales
pos += centers[indexes]

scatter = visuals.Markers()
scatter.set_data(pos, edge_color=None, face_color=(1, 1, 1, 0.3), size=5)
vb3.add(scatter)

grid2 = visuals.GridLines(parent=vb3.scene)


# Add helpful text
text = visuals.Text("mouse wheel = zoom", pos=(100, 15), font_size=14, 
                    color='white', parent=canvas.scene)


if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
