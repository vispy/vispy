# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
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
    """
    def __init__(self, *args, **kwds):
        self.mag = MagnifyTransform()
        self.mag_target = 3
        self.mag._mag = self.mag_target
        self.mouse_pos = None
        self.timer = app.Timer(interval=0.016, connect=self.on_timer)
        super(MagCamera, self).__init__(*args, **kwds)

    def view_mouse_event(self, event):
        self.mouse_pos = event.pos[:2]
        if event.type == 'mouse_wheel':
            m = self.mag_target 
            m *= 1.2 ** event.delta[1]
            m = m if m > 1 else 1
            self.mag_target = m
        else:
            super(MagCamera, self).view_mouse_event(event)
        self.on_timer()
        self.timer.start()
        self._update_transform()
    
    def on_timer(self, event=None):
        c = np.array(self.mag.center)
        if event is None:
            dt = 0.001
        else:
            dt = event.dt
        s = 0.0001**dt
        c1 = c * s + self.mouse_pos * (1-s)
        
        m = self.mag.mag * s + self.mag_target * (1-s)
        
        if (np.all(np.abs((c - c1) / c1) < 1e-5) and 
                (np.abs(np.log(m / self.mag.mag)) < 1e-3)):
            self.timer.stop()
            
        self.mag.center = c1
        self.mag.mag = m
            
        self._update_transform()
    
    def _set_scene_transform(self, tr):
        vbs = self.viewbox.size
        r = min(vbs) / 2
        self.mag.radii = r*0.7, r
        super(MagCamera, self)._set_scene_transform(self.mag * tr)


class Mag1DCamera(MagCamera):
    def __init__(self, *args, **kwds):
        super(Mag1DCamera, self).__init__(*args, **kwds)
        self.mag = Magnify1DTransform()
        self.mag._mag = 3

    def _set_scene_transform(self, tr):
        vbs = self.viewbox.size
        r = vbs[0] / 4
        self.mag.radii = r*0.7, r 
        super(MagCamera, self)._set_scene_transform(self.mag * tr)


canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
grid = canvas.central_widget.add_grid()

vb1 = grid.add_view(row=0, col=0, col_span=2)
vb2 = grid.add_view(row=1, col=0)
vb3 = grid.add_view(row=1, col=1)

#
# Top viewbox: Show a plot line containing fine structure with a 1D 
# magnigication transform.
#
vb1.camera = Mag1DCamera()
pos = np.empty((100000, 2))
pos[:, 0] = np.arange(100000)
pos[:, 1] = np.random.normal(size=100000, loc=50, scale=10)
pos[:, 1] = filter.gaussian_filter(pos[:, 1], 20)
pos[:, 1] += np.random.normal(size=100000, loc=0, scale=2)
pos[:, 1][pos[:, 1] > 55] += 100
pos[:, 1] = filter.gaussian_filter(pos[:, 1], 2)
line = visuals.Line(pos, color='white', parent=vb1.scene)
line.transform = STTransform(translate=(0, 0, -0.1))
vb1.camera.rect = 0, 30, 100000, 100

grid1 = visuals.GridLines(parent=vb1.scene)


#
# Bottom-left viewbox: Image with circular magnification lens.
#
img_data = np.random.normal(size=(100, 100, 3), loc=58,
                            scale=20).astype(np.ubyte)

image = visuals.Image(img_data, method='impostor', grid=(100, 100), 
                      parent=vb2.scene)
vb2.camera = MagCamera()
vb2.camera.rect = (-10, -10, image.size[0]+20, image.size[1]+20) 


#
# Bottom-right viewbox: Scatter plot with many clusters of varying scale.
#
centers = np.random.normal(size=(50, 2))
pos = np.random.normal(size=(100000, 2), scale=0.2)

indexes = np.random.normal(size=100000, loc=centers.shape[0]/2., 
                           scale=centers.shape[0]/3.)
indexes = np.clip(indexes, 0, centers.shape[0]-1).astype(int)
scales = np.log10(np.linspace(-2, 1, centers.shape[0]))[indexes][:, np.newaxis]

pos *= scales
pos += centers[indexes]

vb3.camera = MagCamera()
scatter = visuals.Markers()
scatter.set_data(pos, edge_color=None, face_color=(1, 1, 1, 0.3), size=5)
vb3.add(scatter)
vb3.camera.rect = (-5, -5, 10, 10)
grid2 = visuals.GridLines(parent=vb3.scene)

# Add helpful text
text = visuals.Text("mouse wheel = zoom", pos=(100, 15), font_size=14, 
                    color='white', parent=canvas.scene)


if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
