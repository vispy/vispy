#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
This example demonstrates how to draw 3d-vectors and apply rotation/translation and scaling with time
"""
import os,sys
import numpy as np
from vispy import app, scene
from vispy.visuals.transforms import MatrixTransform

graphics_objects = []

class mbVector(scene.visuals.Vector):
    """
    a simple wrapper class which includes the transformation done on the vector
    """
    def __init__(self, view, face_color, state_vec, orient_vec):
        super(mbVector, self).__init__(10, 10, 0.05, 1., 0.1, 0.25, color=face_color, shading=None, parent=view)
        self.unfreeze()
        self.n = 0
        self.n_max = len(state_vec)
        self.trafo = MatrixTransform()
        self.state_vec = state_vec
        self.orient_vec = orient_vec

    def _update(self):
        """
        update

        called for every time-step
        """
        self.n += 1
        if self.n > self.n_max-1:
            self.n = 0
            return
           
        # first flip the vector in the x direction, such that further rotations are handled correctly
        self.trafo.set_rotation((0,0,1,0,1,0,1,0,0))

        # calculates the scaling of the object on bases of the orientation vector
        scale_x = self.orient_vec[self.n][0]
        scale_y = self.orient_vec[self.n][1] 
        scale_z = self.orient_vec[self.n][2]
        scale = np.sqrt(scale_x*scale_x+scale_y*scale_y+scale_z*scale_z)
        scale = (scale, 1., 1.)

        # calculates the translation of the object on bases of the state vector
        dx = self.state_vec[self.n][0]
        dy = self.state_vec[self.n][1] 
        dz = self.state_vec[self.n][2]
        
        # calculates the rotation (orthogonal O3 Trafo) on bases of the orientation vector)
        ex, ey, ez = self._get_ortho_base((scale_x, scale_y, scale_z))
        new_base = (*ex,*ey,*ez)

        self._doTrafo( dx,dy,dz, base=new_base , scale=scale, reset=False)

    def _doTrafo(self, x=0.,y=0.,z=0., base=None, scale=None, reset=True):
        """
        doing first the scale then rotation and afterwards translate
        """
        if reset:
            self.trafo.reset()
        if scale is not None:
            self.trafo.scale(scale)
        if base is not None:
            self.trafo.mult_rotation(base)
        self.trafo.translate((x,y,z))
        self.transform = self.trafo

    def _norm(self, n):
        """ normalizing a vector n = (x,y,z) """
        x, y, z = n
        norm = np.sqrt(x*x + y*y + z*z)
        return x/norm, y/norm, z/norm

    def _cross(self, n0, n1):
        """ doing a crossproduct i.e. n1 x n2 """
        x0, y0, z0 = n0
        x1, y1, z1 = n1
        x = y0*z1 - z0*y1
        y = z0*x1 - x0*z1
        z = x0*y1 - y0*x1
        return x,y,z

    def _ortho(self, n):
        """ finding an arbitrary orthogonal vector to another in 3d """
        x,y,z = n
        if z!=0. and y!=0.:
            return 0., z, -y
        elif x!=0. and y!=0.:
            return y, -x, 0.
        elif x!=0. and z!=0.:
            return z, 0., -x
        elif x==0 and y==0:
            return 1.,0.,0.
        elif x==0 and z==0:
            return 1.,0.,0.
        elif y==0 and z==0:
            return 0.,1.,0.
        else:
            return 0.,0.,0.

    def _get_ortho_base(self, n):
        """ 
        calc an ottho base for one direction, such that ex is pointing in the end to that direction 
        """
        ex = self._norm(n)        
        ey = self._norm(self._ortho(ex))
        ez = self._cross(ex, ey)
        return ex, ey, ez

class mbCanvas(scene.SceneCanvas):
    """
    A scene canvas class with some add-ons
    """
    def __init__(self):
        super(mbCanvas, self).__init__( keys='interactive', bgcolor='white',
                           size=(800, 600), show=True)

        self.unfreeze()

        # initialize a timer
        self.tt = 0.
        self.timer = app.Timer(interval='auto')
        self.timer.connect(self.on_timer)
        
        # adds a viewbox to the canvas-central-widget
        self.view = self.central_widget.add_view()

        # call the setter for the camera
        self.view.camera = 'arcball'    
        self.view.camera.set_range(x=[-6, 6])

        self.timer.start()
    # ---------------------------------
    def on_key_press(self, event):
        """
        event is included in the parent canvas. here used to start/stop the animation loop
        """
        if event.text == ' ':
            if self.timer.running:
                self.timer.stop()
            else:
                self.timer.start()

    # ---------------------------------
    def on_timer(self, event):
        """
        the update frame function, for physical processes must consider the global time
        
        called with interval if possible or mostly in arbitrary time steps
        """
        global graphics_objects
        # in case we need a global time
        self.tt += event.dt
        for obj in graphics_objects:
            obj._update()

if __name__ == '__main__' and sys.flags.interactive == 0:
    canvas = mbCanvas()
    # the time series 
    time = np.linspace(0, 2.*np.pi, 100)    
    # the vector itself
    vx, vy, vz = np.sin(time), np.cos(time), np.ones(100)
    orient_vector = np.transpose(np.vstack((vx,vy,vz)))
    # the vector points from this point
    ox, oy, oz = np.sin(time), np.zeros(100), np.zeros(100)
    state_vector = np.transpose(np.vstack((ox,oy,oz)))
    # append for convience just to the global graphics objects
    graphics_objects.append(mbVector(canvas.view.scene, "red", state_vector, orient_vector))
    canvas.app.run()


