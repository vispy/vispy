# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of LineVisual. 
"""

import numpy as np
import vispy.app
from vispy.gloo import gl
from vispy.visuals.mesh import MeshVisual
from vispy.util.meshdata import MeshData
from vispy.visuals.transforms import STTransform


class Canvas(vispy.app.Canvas):
    def __init__(self):
        # Generate some data to work with
        mdata = MeshData.sphere(10, 20, 0.3)
        
        # Center: Mesh with pre-indexed vertexes, uniform color
        verts = mdata.vertexes(indexed='faces')
        self.mesh1 = MeshVisual(pos=verts, color=(1, 0, 0, 1))
        
        # Top-left: Mesh with pre-indexed vertexes, per-vertex color
        #   Because vertexes are pre-indexed, we get a different color
        #   every time a vertex is visited, resulting in sharp color differences
        #   between edges.
        nv = verts.size//3
        vcolor = np.ones((nv, 4), dtype=np.float32)
        vcolor[:,0] = np.linspace(0, 1, nv)
        vcolor[:,1] = np.linspace(1, 0, nv)
        vcolor[:,2] = np.random.normal(size=nv)
        self.mesh2 = MeshVisual(pos=verts, color=vcolor)
        self.mesh2.transform = STTransform(translate=(-0.5, 0.5))

        # Top-right: Mesh with unindexed vertexes, per-vertex color
        #   Because vertexes are unindexed, we get the same color
        #   every time a vertex is visited, resulting in no color differences
        #   between edges.
        verts = mdata.vertexes()
        faces = mdata.faces()
        nv = verts.size//3
        vcolor = np.ones((nv, 4), dtype=np.float32)
        vcolor[:,0] = np.linspace(0, 1, nv)
        vcolor[:,1] = np.linspace(1, 0, nv)
        vcolor[:,2] = np.random.normal(size=nv)
        self.mesh3 = MeshVisual(pos=verts, faces=faces, color=vcolor)
        self.mesh3.transform = STTransform(translate=(0.5, 0.5))
        
        vispy.app.Canvas.__init__(self)
        self.size = (800, 800)
        self.show()
        
    def on_paint(self, ev):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glViewport(0, 0, *self.size)
        self.mesh1.paint()
        self.mesh2.paint()
        self.mesh3.paint()
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
    


