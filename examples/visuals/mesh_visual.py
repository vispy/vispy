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
        mdata = MeshData.sphere(10, 20, 0.3)
        verts = mdata.vertexes(indexed='faces')
        self.mesh1 = MeshVisual(pos=verts)
        
        nv = verts.size//3
        color = np.ones((nv, 4), dtype=np.float32)
        color[:,0] = np.linspace(0, 1, nv)
        color[:,1] = np.linspace(1, 0, nv)
        self.mesh2 = MeshVisual(pos=verts, color=color)
        self.mesh2.transform = STTransform(translate=(0.5, 0.5))
        
        vispy.app.Canvas.__init__(self)
        self.size = (800, 800)
        self.show()
        
    def on_paint(self, ev):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glViewport(0, 0, *self.size)
        self.mesh1.paint()
        self.mesh2.paint()
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
    


