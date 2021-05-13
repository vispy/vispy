#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 30

"""
Demonstration of boids simulation. Boids is an artificial life
program, developed by Craig Reynolds in 1986, which simulates the
flocking behaviour of birds.
Based on code from glumpy by Nicolas Rougier.
"""

import time

import numpy as np
from scipy.spatial import cKDTree

from vispy import gloo
from vispy import app

VERT_SHADER = """
#version 120
attribute vec3 position;
attribute vec4 color;
attribute float size;

varying vec4 v_color;
void main (void) {
    gl_Position = vec4(position, 1.0);
    v_color = color;
    gl_PointSize = size;
}
"""

FRAG_SHADER = """
#version 120
varying vec4 v_color;
void main()
{
    float x = 2.0*gl_PointCoord.x - 1.0;
    float y = 2.0*gl_PointCoord.y - 1.0;
    float a = 1.0 - (x*x + y*y);
    gl_FragColor = vec4(v_color.rgb, a*v_color.a);
}

"""


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive')

        ps = self.pixel_scale

        # Create boids
        n = 1000
        size_type = ('size', 'f4', 1*ps) if ps > 1 else ('size', 'f4')
        self.particles = np.zeros(2 + n, [('position', 'f4', 3),
                                          ('position_1', 'f4', 3),
                                          ('position_2', 'f4', 3),
                                          ('velocity', 'f4', 3),
                                          ('color', 'f4', 4),
                                          size_type])
        self.boids = self.particles[2:]
        self.target = self.particles[0]
        self.predator = self.particles[1]

        self.boids['position'] = np.random.uniform(-0.25, +0.25, (n, 3))
        self.boids['velocity'] = np.random.uniform(-0.00, +0.00, (n, 3))
        self.boids['size'] = 4*ps
        self.boids['color'] = 1, 1, 1, 1

        self.target['size'] = 16*ps
        self.target['color'][:] = 1, 1, 0, 1
        self.predator['size'] = 16*ps
        self.predator['color'][:] = 1, 0, 0, 1
        self.target['position'][:] = 0.25, 0.0, 0

        # Time
        self._t = time.time()
        self._pos = 0.0, 0.0
        self._button = None

        width, height = self.physical_size
        gloo.set_viewport(0, 0, width, height)

        # Create program
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)

        # Create vertex buffers
        self.vbo_position = gloo.VertexBuffer(self.particles['position']
                                              .copy())
        self.vbo_color = gloo.VertexBuffer(self.particles['color'].copy())
        self.vbo_size = gloo.VertexBuffer(self.particles['size'].copy())

        # Bind vertex buffers
        self.program['color'] = self.vbo_color
        self.program['size'] = self.vbo_size
        self.program['position'] = self.vbo_position

        gloo.set_state(clear_color=(0, 0, 0, 1), blend=True,
                       blend_func=('src_alpha', 'one'))

        self._timer = app.Timer('auto', connect=self.update, start=True)

        self.show()

    def on_resize(self, event):
        width, height = event.physical_size
        gloo.set_viewport(0, 0, width, height)

    def on_mouse_press(self, event):
        self._button = event.button
        self.on_mouse_move(event)

    def on_mouse_release(self, event):
        self._button = None
        self.on_mouse_move(event)

    def on_mouse_move(self, event):
        if not self._button:
            return
        w, h = self.size
        x, y = event.pos
        sx = 2 * x / float(w) - 1.0
        sy = - (2 * y / float(h) - 1.0)

        if self._button == 1:
            self.target['position'][:] = sx, sy, 0
        elif self._button == 2:
            self.predator['position'][:] = sx, sy, 0

    def on_draw(self, event):
        gloo.clear()
        # Draw
        self.program.draw('points')
        # Next iteration
        self._t = self.iteration(time.time() - self._t)

    def iteration(self, dt):
        t = self._t

        t += 0.5 * dt
        # self.target[...] = np.array([np.sin(t),np.sin(2*t),np.cos(3*t)])*.1

        t += 0.5 * dt
        # self.predator[...] = np.array([np.sin(t),np.sin(2*t),np.cos(3*t)])*.2

        self.boids['position_2'] = self.boids['position_1']
        self.boids['position_1'] = self.boids['position']
        n = len(self.boids)
        P = self.boids['position']
        V = self.boids['velocity']

        # Cohesion: steer to move toward the average position of local
        # flockmates
        C = -(P - P.sum(axis=0) / n)

        # Alignment: steer towards the average heading of local flockmates
        A = -(V - V.sum(axis=0) / n)

        # Repulsion: steer to avoid crowding local flockmates
        D, idxs = cKDTree(P).query(P, 5)
        M = np.repeat(D < 0.05, 3, axis=1).reshape(n, 5, 3)
        Z = np.repeat(P, 5, axis=0).reshape(n, 5, 3)
        R = -((P[idxs] - Z) * M).sum(axis=1)

        # Target : Follow target
        T = self.target['position'] - P

        # Predator : Move away from predator
        dP = P - self.predator['position']
        D = np.maximum(0, 0.3 -
                       np.sqrt(dP[:, 0] ** 2 +
                               dP[:, 1] ** 2 +
                               dP[:, 2] ** 2))
        D = np.repeat(D, 3, axis=0).reshape(n, 3)
        dP *= D

        # self.boids['velocity'] += 0.0005*C + 0.01*A + 0.01*R +
        #                           0.0005*T + 0.0025*dP
        self.boids['velocity'] += 0.0005 * C + 0.01 * \
            A + 0.01 * R + 0.0005 * T + 0.025 * dP
        self.boids['position'] += self.boids['velocity']

        self.vbo_position.set_data(self.particles['position'].copy())

        return t


if __name__ == '__main__':
    c = Canvas()
    app.run()
