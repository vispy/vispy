# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of LineVisual. 
"""

import numpy as np
import vispy.app
from vispy.gloo import gl
from vispy.visuals.mesh import (MeshVisual, VertexColorComponent, 
                                GridContourComponent)
from vispy.util.meshdata import MeshData
from vispy.visuals.transforms import STTransform


class Canvas(vispy.app.Canvas):
    def __init__(self):
        self.meshes = []
        
        # Generate some data to work with
        mdata = MeshData.sphere(10, 20, 0.3)
        
        # Center: Mesh with pre-indexed vertexes, uniform color
        verts = mdata.vertexes(indexed='faces')
        mesh = MeshVisual(pos=verts, color=(1, 0, 0, 1))
        self.meshes.append(mesh)
        
        # Top-left: Mesh with pre-indexed vertexes, per-face color
        #   Because vertexes are pre-indexed, we get a different color
        #   every time a vertex is visited, resulting in sharp color differences
        #   between edges.
        nf = verts.size//9
        fcolor = np.ones((nf, 3, 4), dtype=np.float32)
        fcolor[...,0] = np.linspace(0, 1, nf)[:, np.newaxis]
        fcolor[...,1] = np.linspace(1, 0, nf)[:, np.newaxis]
        fcolor[...,2] = np.random.normal(size=nf)[:, np.newaxis]
        mesh = MeshVisual(pos=verts, color=fcolor)
        mesh.transform = STTransform(translate=(-0.5, 0.5))
        self.meshes.append(mesh)        

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
        mesh = MeshVisual(pos=verts, faces=faces, color=vcolor)
        mesh.transform = STTransform(translate=(0.5, 0.5))
        self.meshes.append(mesh)
        
        # Bottom-left: Mesh colored by vertexes + grid contours
        mesh = MeshVisual(pos=verts, faces=faces)
        mesh.transform = STTransform(translate=(-0.5, -0.5))
        mesh.fragment_components = [VertexColorComponent(vcolor), 
                                    GridContourComponent(
                                        spacing=(0.1, 0.1, 0.1))]
        self.meshes.append(mesh)
        
        
        
        vispy.app.Canvas.__init__(self)
        self.size = (800, 800)
        self.show()
        
    def on_paint(self, ev):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glViewport(0, 0, *self.size)
        for mesh in self.meshes:
            mesh.paint()
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
    


