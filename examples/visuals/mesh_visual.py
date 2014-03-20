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
                                GridContourComponent, VertexNormalComponent,
                                ShadingComponent)
from vispy.util.meshdata import MeshData
from vispy.visuals.transforms import (STTransform, AffineTransform, 
                                      ChainTransform)


class Canvas(vispy.app.Canvas):
    def __init__(self):
        self.meshes = []
        self.rotation = AffineTransform()
        
        # Generate some data to work with
        global mdata
        mdata = MeshData.sphere(20, 40, 0.3)
        
        # Center: Mesh with pre-indexed vertexes, uniform color
        verts = mdata.vertexes(indexed='faces')
        mesh = MeshVisual(pos=verts, color=(1, 0, 0, 1))
        mesh.transform = ChainTransform([self.rotation,
                                         STTransform(translate=(0.0, 0.0)),
                                         ], simplify=False)
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
        mesh.transform = ChainTransform([self.rotation,
                                         STTransform(translate=(-0.5, 0.5)),
                                         ], simplify=False)
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
        mesh.transform = ChainTransform([self.rotation,
                                         STTransform(translate=(0.5, 0.5)),
                                         ], simplify=False)
        self.meshes.append(mesh)
        
        # Bottom-left: Mesh colored by vertexes + grid contours
        mesh = MeshVisual(pos=verts, faces=faces)
        mesh.transform = ChainTransform([self.rotation,
                                         STTransform(translate=(-0.5, -0.5)),
                                         ], simplify=False)
        mesh.fragment_components = [VertexColorComponent(vcolor), 
                                    GridContourComponent(
                                        spacing=(0.13, 0.13, 0.13))]
        self.meshes.append(mesh)
        
        # Bottom-right: Phong shaded mesh
        mesh = MeshVisual(pos=verts, faces=faces)
        mesh.transform = ChainTransform([self.rotation,
                                         STTransform(translate=(0.5, -0.5)),
                                         ], simplify=False)
        normal_comp = VertexNormalComponent(mdata)
        mesh.fragment_components = [VertexColorComponent(vcolor), 
                                    normal_comp, # TODO: should the shading component take care of this?
                                    GridContourComponent(
                                        spacing=(0.1, 0.1, 0.1)),
                                    ShadingComponent(
                                        normal_comp,
                                        lights=[((-1, 1, -1), (1.0, 1.0, 1.0))],
                                        ambient=0.2)]
        self.meshes.append(mesh)
        
        vispy.app.Canvas.__init__(self)
        self.size = (800, 800)
        self.show()
        
        self.timer = vispy.app.Timer(connect=self.rotate)
        self.timer.start(0.016)
        
    def rotate(self, event):
        self.rotation.rotate(1, (0,1,0))
        # TODO: altering rotation should trigger this automatically.
        for m in self.meshes:
            m._program._need_build = True
        self.update()
        
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
    


