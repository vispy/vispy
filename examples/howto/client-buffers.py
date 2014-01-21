# !/usr/bin/env python
# -*- coding: utf-8 -*-
# This code of this example should be considered public domain.

"""
This is the boids demo coded using a client buffer. This means that
the data is *not* stored on the GPU in a vertex buffer object, but
instead send to the GPU on each draw.

Note that in general you should avoid client buffers and use
vertex buffers. This is example just demonstrates the technique.

In this particular example the attribute data is updated on each draw,
so the performance of both methods should be more or less similar.

The main difference is that one should use the ``client=True`` keyword
argument when creating a VertexBuffer or ElementBuffer.

"""

import time
import numpy as np
from scipy.spatial import cKDTree

from vispy.gloo import gl
from vispy import app
from vispy.gloo import Program, VertexBuffer


# Create boids
n = 1000
particles = np.zeros(2 + n, [('position', 'f4', 3),
                             ('position_1', 'f4', 3),
                             ('position_2', 'f4', 3),
                             ('velocity', 'f4', 3),
                             ('color', 'f4', 4),
                             ('size', 'f4', 1)])
boids = particles[2:]
target = particles[0]
predator = particles[1]

boids['position'] = np.random.uniform(-0.25, +0.25, (n, 3))
boids['velocity'] = np.random.uniform(-0.00, +0.00, (n, 3))
boids['size'] = 4
boids['color'] = 1, 1, 1, 1

target['size'] = 16
target['color'][:] = 1, 1, 0, 1
predator['size'] = 16
predator['color'][:] = 1, 0, 0, 1


VERT_SHADER = """
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
        app.Canvas.__init__(self)

        # Time
        self._t = time.time()
        self._pos = 0.0, 0.0
        self._button = None

        # Create program
        self.program = Program(VERT_SHADER, FRAG_SHADER)
        self.program['color'] = VertexBuffer(particles['color'], client=True)
        self.program['size'] = VertexBuffer(particles['size'], client=True)

    def on_initialize(self, event):
        gl.glClearColor(0, 0, 0, 1)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)

    def on_resize(self, event):
        width, height = event.size
        gl.glViewport(0, 0, width, height)

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
            target['position'][:] = sx, sy, 0
        elif self._button == 2:
            predator['position'][:] = sx, sy, 0

    def on_paint(self, event):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Draw
        self.program['position'] = VertexBuffer(
            particles['position'],
            client=True)
        self.program.draw(gl.GL_POINTS)

        # Next iteration
        self._t = self.iteration(time.time() - self._t)

        # Invoke a new draw
        self.update()

    def iteration(self, dt):
        t = self._t

        t += 0.5 * dt
        #target[...] = np.array([np.sin(t),np.sin(2*t),np.cos(3*t)])*.1

        t += 0.5 * dt
        #predator[...] = np.array([np.sin(t),np.sin(2*t),np.cos(3*t)])*.2

        boids['position_2'] = boids['position_1']
        boids['position_1'] = boids['position']
        n = len(boids)
        P = boids['position']
        V = boids['velocity']

        # Cohesion: steer to move toward the average position of local
        # flockmates
        C = -(P - P.sum(axis=0) / n)

        # Alignment: steer towards the average heading of local flockmates
        A = -(V - V.sum(axis=0) / n)

        # Repulsion: steer to avoid crowding local flockmates
        D, I = cKDTree(P).query(P, 5)
        M = np.repeat(D < 0.05, 3, axis=1).reshape(n, 5, 3)
        Z = np.repeat(P, 5, axis=0).reshape(n, 5, 3)
        R = -((P[I] - Z) * M).sum(axis=1)

        # Target : Follow target
        T = target['position'] - P

        # Predator : Move away from predator
        dP = P - predator['position']
        D = np.maximum(0, 0.3 -
                       np.sqrt(dP[:, 0] ** 2 +
                               dP[:, 1] ** 2 +
                               dP[:, 2] ** 2))
        D = np.repeat(D, 3, axis=0).reshape(n, 3)
        dP *= D

        #boids['velocity'] += 0.0005*C + 0.01*A + 0.01*R + 0.0005*T + 0.0025*dP
        boids['velocity'] += 0.0005 * C + 0.01 * \
            A + 0.01 * R + 0.0005 * T + 0.025 * dP
        boids['position'] += boids['velocity']

        return t


if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()
