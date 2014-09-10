# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# vispy: gallery 30

"""
Simple demonstration of LineVisual.
"""

import numpy as np
import vispy.app
from vispy import gloo
from vispy.scene.visuals.modular_mesh import ModularMesh
from vispy.scene.components import (VertexColorComponent, GridContourComponent,
                                    VertexNormalComponent, ShadingComponent)
from vispy.geometry import create_sphere
from vispy.scene.transforms import (STTransform, AffineTransform,
                                    ChainTransform)


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        self.meshes = []
        self.rotation = AffineTransform()

        # Generate some data to work with
        global mdata
        mdata = create_sphere(20, 40, 1.0)

        # Mesh with pre-indexed vertices, uniform color
        verts = mdata.get_vertices(indexed='faces')
        mesh = ModularMesh(pos=verts, color=(1, 0, 0, 1))
        self.meshes.append(mesh)

        # Mesh with pre-indexed vertices, per-face color
        #   Because vertices are pre-indexed, we get a different color
        #   every time a vertex is visited, resulting in sharp color
        #   differences between edges.
        nf = verts.size//9
        fcolor = np.ones((nf, 3, 4), dtype=np.float32)
        fcolor[..., 0] = np.linspace(1, 0, nf)[:, np.newaxis]
        fcolor[..., 1] = np.random.normal(size=nf)[:, np.newaxis]
        fcolor[..., 2] = np.linspace(0, 1, nf)[:, np.newaxis]
        mesh = ModularMesh(pos=verts, color=fcolor)
        self.meshes.append(mesh)

        # Mesh with unindexed vertices, per-vertex color
        #   Because vertices are unindexed, we get the same color
        #   every time a vertex is visited, resulting in no color differences
        #   between edges.
        verts = mdata.get_vertices()
        faces = mdata.get_faces()
        nv = verts.size//3
        vcolor = np.ones((nv, 4), dtype=np.float32)
        vcolor[:, 0] = np.linspace(1, 0, nv)
        vcolor[:, 1] = np.random.normal(size=nv)
        vcolor[:, 2] = np.linspace(0, 1, nv)
        mesh = ModularMesh(pos=verts, faces=faces, color=vcolor)
        self.meshes.append(mesh)

        # Mesh colored by vertices + grid contours
        mesh = ModularMesh(pos=verts, faces=faces)
        mesh.color_components = [VertexColorComponent(vcolor),
                                 GridContourComponent(spacing=(0.13, 0.13,
                                                               0.13))]
        self.meshes.append(mesh)

        # Phong shaded mesh
        mesh = ModularMesh(pos=verts, faces=faces)
        normal_comp = VertexNormalComponent(mdata)
        mesh.color_components = [VertexColorComponent(vcolor),
                                 GridContourComponent(spacing=(0.1, 0.1, 0.1)),
                                 ShadingComponent(normal_comp,
                                                  lights=[((-1, 1, -1),
                                                          (1.0, 1.0, 1.0))],
                                                  ambient=0.2)]
        self.meshes.append(mesh)

        # Phong shaded mesh, flat faces
        mesh = ModularMesh(pos=mdata.get_vertices(indexed='faces'))
        normal_comp = VertexNormalComponent(mdata, smooth=False)
        mesh.color_components = [
            VertexColorComponent(vcolor[mdata.get_faces()]),
            GridContourComponent(spacing=(0.1, 0.1, 0.1)),
            ShadingComponent(normal_comp, lights=[((-1, 1, -1),
                                                  (1.0, 1.0, 1.0))],
                             ambient=0.2)]
        self.meshes.append(mesh)

        # Lay out meshes in a grid
        grid = (3, 3)
        s = 300. / max(grid)
        for i, mesh in enumerate(self.meshes):
            x = 800. * (i % grid[0]) / grid[0] + 400. / grid[0] - 2
            y = 800. * (i // grid[1]) / grid[1] + 400. / grid[1] + 2
            mesh.transform = ChainTransform([STTransform(translate=(x, y),
                                                         scale=(s, s, 1)),
                                             self.rotation])

        vispy.scene.SceneCanvas.__init__(self, keys='interactive')

        self.size = (800, 800)
        self.show()

        self.timer = vispy.app.Timer(connect=self.rotate)
        self.timer.start(0.016)

    def rotate(self, event):
        self.rotation.rotate(1, (0, 1, 0))
        # TODO: altering rotation should trigger this automatically.
        for m in self.meshes:
            m._program._need_build = True
        self.update()

    def on_draw(self, ev):
        gloo.set_clear_color('black')
        gloo.clear(color=True, depth=True)
        for mesh in self.meshes:
            self.draw_visual(mesh)


if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
