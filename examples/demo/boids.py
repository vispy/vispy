# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code of this example should be considered public domain.

""" 
Demonstration of boids simulation. Boids is an artificial life
program, developed by Craig Reynolds in 1986, which simulates the
flocking behaviour of birds.
Based on code from glumpy by Nicolas Rougier.
"""

import time

import numpy as np
from scipy.spatial import cKDTree

from vispy import gl
from vispy import oogl
from vispy import app



# Create boids
n = 1000
boids = np.zeros(n, [   ('position',   'f4', 3),
                        ('position_1', 'f4', 3),
                        ('position_2', 'f4', 3),
                        ('velocity',   'f4', 3)] )
boids['position'] = np.random.uniform(-0.25, +0.25, (n,3))
boids['velocity'] = np.random.uniform(-0.00, +0.00, (n,3))

# Target and predator
target   = np.zeros(3)
predator = np.zeros(3)


VERT_SHADER = """ // simple vertex shader
#version 120
attribute vec3 position;
uniform vec3 u_color;
uniform float u_size;
varying vec3 v_color;
void main (void) {
    // Calculate position
    gl_Position = vec4(position.x, position.y, position.z, 1.0);
    v_color = u_color;
    gl_PointSize = u_size;
}
"""

FRAG_SHADER = """ // simple fragment shader
#version 120
varying vec3 v_color;
void main()
{    
    float x = 2.0*gl_PointCoord.x - 1.0;
    float y = 2.0*gl_PointCoord.y - 1.0;
    float a = 1.0 - (x*x + y*y);
    gl_FragColor = vec4(v_color, a);
}

"""


class Canvas(app.Canvas):
    
    def __init__(self):
        app.Canvas.__init__(self)
        
        # Time
        self._t = time.time()
        self._pos = 0.0, 0.0
        self._button = None
        
        # Create program
        self._program = oogl.Program(VERT_SHADER, FRAG_SHADER)
    
    def on_initialize(self, event):
        gl.glClearColor(0,0,0,1);
        
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)
        
        # todo: normal GL requires these lines, ES 2.0 does not
        from OpenGL import GL
        gl.glEnable(GL.GL_VERTEX_PROGRAM_POINT_SIZE)
        gl.glEnable(GL.GL_POINT_SPRITE)
    
    def on_resize(self, event):
        gl.glViewport(0, 0, *self.geometry[2:])
        
    def on_mouse_press(self, event):
        self._button = event.button
        self.on_mouse_move(event)
    
    def on_mouse_release(self, event):
        self._button = None
        self.on_mouse_move(event)
    
    def on_mouse_move(self, event):
        if not self._button:
            return
        w, h = self.geometry[2:]
        x, y = event.pos
        sx = 2*x/float(w) -1.0
        sy = - (2*y/float(h) -1.0)
        
        if self._button == 1:
            target[0], target[1] = sx, sy
        elif self._button  == 2:
            predator[0], predator[1] = sx, sy
   
    
    def on_paint(self, event):
        
        # Init
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        # Draw
        with self._program as prog:
            prog['u_size'] = 4.0
            prog['u_color'] = 0.0, 1.0, 1.0
            prog['position'] = boids['position']
            prog.draw_arrays(gl.GL_POINTS)
            #
            prog['u_size'] = 16.0
            prog['u_color'] = 0.0, 1.0, 0.0
            prog['position'] = target.reshape((1,3))
            prog.draw_arrays(gl.GL_POINTS)
            #
            prog['u_color'] = 1.0, 0.0, 0.0
            prog['position'] = predator.reshape((1,3))
            prog.draw_arrays(gl.GL_POINTS)
        
        # Next iteration
        self._t = self.iteration(time.time() - self._t)
        # Invoke a new draw
        self.update()
    
    
    def iteration(self, dt):
        t = self._t 
        
        t += 0.5*dt
        #target[...] = np.array([np.sin(t),np.sin(2*t),np.cos(3*t)])*.1
    
        t += 0.5*dt
        #predator[...] = np.array([np.sin(t),np.sin(2*t),np.cos(3*t)])*.2
    
        boids['position_2'] = boids['position_1']
        boids['position_1'] = boids['position']
        n = len(boids)
        P = boids['position']
        V = boids['velocity']
    
        # Cohesion: steer to move toward the average position of local flockmates
        C = -(P - P.sum(axis=0)/n)
    
        # Alignment: steer towards the average heading of local flockmates
        A = -(V - V.sum(axis=0)/n)
    
        # Repulsion: steer to avoid crowding local flockmates
        D,I = cKDTree(P).query(P,5)
        M = np.repeat(D < 0.05, 3, axis=1).reshape(n,5,3)
        Z = np.repeat(P,5,axis=0).reshape(n,5,3)
        R = -((P[I]-Z)*M).sum(axis=1)
    
        # Target : Follow target
        T = target - P
    
        # Predator : Move away from predator
        dP = P - predator
        D = np.maximum(0, 0.3 - np.sqrt(dP[:,0]**2 +dP[:,1]**2+dP[:,2]**2) )
        D = np.repeat(D,3,axis=0).reshape(n,3)
        dP *= D
    
        #boids['velocity'] += 0.0005*C + 0.01*A + 0.01*R + 0.0005*T + 0.0025*dP
        boids['velocity'] += 0.0005*C + 0.01*A + 0.01*R + 0.0005*T + 0.025*dP
        boids['position'] += boids['velocity']
        
        return t


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
    
