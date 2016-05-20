# -*- coding: utf8 -*- 
"""
Debugging system for Triangulation class. Displays stepwise visual 
representation of the algorithm. 

This system currently requires pyqtgraph for its visual output.
"""
from __future__ import division

import numpy as np
import time

from ..util.geometry.triangulation import Triangulation


class DebugTriangulation(Triangulation):
    """ 
    Visualize triangulation process stepwise to aid in debugging.
    
    *interval* specifies the diration to wait before drawing each update in
    the triangulation procedure. Negative values cause the display to wait
    until the user clicks on the window for each update.
    
    *skip* causes the display to immediately process the first N events
    before pausing.
    """
    def __init__(self, pts, edges, interval=0.01, skip=0):
        self.interval = interval
        self.iteration = 0
        self.skip = skip 
        
        Triangulation.__init__(self, pts, edges)
        
        # visual #debugging: draw edges, front, triangles
        self.win = pg.plot()
        self.graph = pg.GraphItem(pos=pts.copy(), adj=edges.copy(), 
                                  pen={'width': 3, 'color': (0, 100, 0)})
        self.win.addItem(self.graph)
        self.front_line = pg.PlotCurveItem(pen={'width': 2, 
                                                'dash': [5, 5], 
                                                'color': 'y'})
        self.win.addItem(self.front_line)
        self.tri_shapes = {}
        
        self.nextStep = False
        self.win.scene().sigMouseClicked.connect(self.mouseClicked)

    def mouseClicked(self):
        self.nextStep = True
        
    def draw_state(self):
        global app
        print("State %s" % self.iteration)
        self.iteration += 1
        if self.iteration <= self.skip:
            return
        
        front_pts = self.pts[np.array(self.front)]
        self.front_line.setData(front_pts[:, 0], front_pts[:, 1])
        self.graph.setData(pos=self.pts, adj=self.edges) 
        
        # Auto-advance on timer
        if self.interval < 0:
            #Advance once per click
            while True:
                app.processEvents()
                time.sleep(0.01)
                if self.nextStep:
                    self.nextStep = False
                    break
        else:
            # sleep, but keep ui responsive
            for i in range(int(self.interval / 0.01)):
                app.processEvents()
                time.sleep(0.01)
            
    def draw_tri(self, tri, source=None):
        # assign triangle color based on the source that generated it
        color = {
            None: (0, 255, 255, 50),
            'smooth1': (0, 255, 0, 50),
            'fill_hull': (255, 255, 0, 50),
            'edge_event': (100, 100, 255, 100),
        }[source]
        
        tpts = self.pts[np.array(tri)]
        path = pg.arrayToQPath(tpts[:, 0], tpts[:, 1])
        shape = pg.QtGui.QGraphicsPathItem(path)
        shape.setPen(pg.mkPen(255, 255, 255, 100))
        brush = pg.mkBrush(color)
        shape.setBrush(brush)
        self.win.addItem(shape)
        self.tri_shapes[tri] = shape
        self.draw_state()

    def undraw_tri(self, tri):
        shape = self.tri_shapes.pop(tri)
        self.win.removeItem(shape)
        self.draw_state()
        
    def add_tri(self, *args, **kwargs):
        Triangulation._add_tri(self, *args, **kwargs)
        self.draw_tri(list(self.tris.keys())[-1], 
                      source=kwargs.get('source', None))
    
    def remove_tri(self, *args, **kwargs):
        k = Triangulation._remove_tri(self, *args, **kwargs)
        self.undraw_tri(k)

    def edge_event(self, *args, **kwargs):
        self.draw_state()
        Triangulation._edge_event(self, *args, **kwargs)
        self.draw_state()


if __name__ == '__main__':
    import pyqtgraph as pg
    
    app = pg.mkQApp()
    
    #user input data - points and constraining edges
    
    #
    #  Test 1
    #
    pts = [(0, 0),
           (10, 0),
           (10, 10),
           (20, 10),
           (20, 20),
           (25, 20),
           (25, 25),
           (20, 25),
           (20, 20),
           (10, 17),
           (5, 25),
           (9, 30),
           (6, 15),
           (15, 12.5),
           (0, 5)]
    l = len(pts)
    edges = [(i, (i+1) % l) for i in range(l)]
    pts += [(21, 21),
            (24, 21),
            (24, 24),
            (21, 24)]
    edges += [(l,   l+1),
              (l+1, l+2),
              (l+2, l+3),
              (l+3, l)]

    pts = np.array(pts, dtype=float)
    edges = np.array(edges, dtype=int)

    #t = DebugTriangulation(pts, edges, interval=-1, skip=19570)
    #t.triangulate()

    # make lines that are entirely vertical / horizontal
    np.random.seed(1)
    N = 100
    pts = [[0, 0]]
    for i in range(N - 1):
        p = pts[-1][:]
        p[i % 2] += np.random.normal()
        pts.append(p)
    pts = np.array(pts)
    edges = np.zeros((N, 2), dtype=int)
    edges[:, 0] = np.arange(N)
    edges[:, 1] = np.arange(1, N + 1) % N
    t = DebugTriangulation(pts, edges)
    t.triangulate()
