# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstration of various features of Line visual.
"""

import numpy as np
import vispy.app
from vispy import gloo
from vispy.scene import visuals
from vispy.scene.transforms import STTransform

# vertex positions of data to draw
N = 200
pos = np.zeros((N, 2), dtype=np.float32)
pos[:, 0] = np.linspace(10, 390, N)
pos[:, 1] = np.random.normal(size=N, scale=30, loc=0)

# color array
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]

# connection array
connect = np.empty((N-1, 2), np.int32)
connect[:, 0] = np.arange(N-1)
connect[:, 1] = connect[:, 0] + 1
connect[N/2, 1] = N/2  # put a break in the middle


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        
        # Create several visuals demonstrating different 
        # features of Line
        self.lines = [
            #
            # agg-mode lines:
            #
            
            # solid color
            visuals.Line(pos=pos, color=(0, 0.5, 0.3, 1)),
            
            # wide
            visuals.Line(pos=pos, color=(0, 0.5, 0.3, 1), width=5),
            
            #
            # GL-mode lines:
            #
            
            # solid color
            visuals.Line(pos=pos, color=(0, 0.5, 0.3, 1), mode='gl'),
            
            # per-vertex color
            visuals.Line(pos=pos, color=color, mode='gl'),
            
            # updating (see the "update" function below)
            visuals.Line(pos=pos, color=color, mode='gl'),
            
            # only connect alternate pairs of vertices
            visuals.Line(pos=pos, color=(0, 0.5, 0.3, 1), connect='segments', 
                         mode='gl'),
            
            # connect specific pairs of vertices, specified in an adjacency
            # matrix
            visuals.Line(pos=pos, color=(0, 0.5, 0.3, 1), connect=connect, 
                         mode='gl'),
            
            # gl-mode width
            visuals.Line(pos=pos, color=(0, 0.5, 0.3, 1), width=4, 
                         antialias=False, mode='gl'),
            
        ]
        
        for i,line in enumerate(self.lines):
            # arrange lines in a grid
            x = 400 * (i % 2)
            y = 160 * ((i // 2) + 1)
            line.transform = STTransform(translate=[x, y])
            
            # redraw the canvas if any visuals request an update
            line.events.update.connect(self.line_changed)

        vispy.scene.SceneCanvas.__init__(self, keys='interactive')
        self.size = (800, 800)
        self.show()

    def line_changed(self, ev):
        self.update()

    def on_draw(self, ev):
        gloo.set_clear_color('black')
        gloo.clear(color=True, depth=True)
        for line in self.lines:
            self.draw_visual(line)


if __name__ == '__main__':
    win = Canvas()

    def update(ev):
        pos[:, 1] = np.random.normal(size=N, scale=30, loc=0)
        win.lines[4].set_data(pos=pos)

    timer = vispy.app.Timer()
    timer.connect(update)
    timer.start(0)
    
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
