# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstration of animated LineVisual.
"""

import numpy as np
import vispy.app
from vispy.gloo import gl
from vispy.scene import visuals

# vertex positions of data to draw
N = 200
pos = np.zeros((N, 3), dtype=np.float32)
pos[:, 0] = np.linspace(-0.9, 0.9, N)
pos[:, 1] = np.random.normal(size=N, scale=0.2).astype(np.float32)

# color array
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]


class Canvas(vispy.app.Canvas):
    def __init__(self):
        self.line = visuals.Line(pos=pos, color=color)
        self.line.events.update.connect(self.line_changed)

        vispy.app.Canvas.__init__(self, close_keys='escape')
        self.size = (800, 800)
        self.show()

    def line_changed(self, ev):
        self.update()

    def on_draw(self, ev):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glViewport(0, 0, *self.size)
        self.line.paint()


if __name__ == '__main__':
    win = Canvas()

    def update(ev):
        pos[:, 1] = np.random.normal(size=N, scale=0.2)
        win.line.set_data(pos=pos)

    timer = vispy.app.Timer()
    timer.connect(update)
    timer.start(0)
    #update(0)
    #vispy.app.process_events()
    #update(0)
    #vispy.app.process_events()

    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
