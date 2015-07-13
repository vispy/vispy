# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of Mesh visual.
"""

import numpy as np
from vispy import app, gloo, visuals
from vispy.geometry import create_sphere
from vispy.visuals.transforms import (STTransform, MatrixTransform,
                                      ChainTransform)


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=(800, 550))

        self.meshes = []
        self.rotation = MatrixTransform()

        # Generate some data to work with
        global mdata
        mdata = create_sphere(20, 40, 1.0)

        # Mesh with pre-indexed vertices, uniform color
        self.meshes.append(visuals.MeshVisual(meshdata=mdata, color='b'))

        # Mesh with pre-indexed vertices, per-face color
        # Because vertices are pre-indexed, we get a different color
        # every time a vertex is visited, resulting in sharp color
        # differences between edges.
        verts = mdata.get_vertices(indexed='faces')
        nf = verts.size//9
        fcolor = np.ones((nf, 3, 4), dtype=np.float32)
        fcolor[..., 0] = np.linspace(1, 0, nf)[:, np.newaxis]
        fcolor[..., 1] = np.random.normal(size=nf)[:, np.newaxis]
        fcolor[..., 2] = np.linspace(0, 1, nf)[:, np.newaxis]
        mesh = visuals.MeshVisual(vertices=verts, face_colors=fcolor)
        self.meshes.append(mesh)

        # Mesh with unindexed vertices, per-vertex color
        # Because vertices are unindexed, we get the same color
        # every time a vertex is visited, resulting in no color differences
        # between edges.
        verts = mdata.get_vertices()
        faces = mdata.get_faces()
        nv = verts.size//3
        vcolor = np.ones((nv, 4), dtype=np.float32)
        vcolor[:, 0] = np.linspace(1, 0, nv)
        vcolor[:, 1] = np.random.normal(size=nv)
        vcolor[:, 2] = np.linspace(0, 1, nv)
        self.meshes.append(visuals.MeshVisual(verts, faces, vcolor))
        self.meshes.append(visuals.MeshVisual(verts, faces, vcolor,
                                              shading='flat'))
        self.meshes.append(visuals.MeshVisual(verts, faces, vcolor,
                                              shading='smooth'))

        # Lay out meshes in a grid
        grid = (3, 3)
        s = 300. / max(grid)
        for i, mesh in enumerate(self.meshes):
            x = 800. * (i % grid[0]) / grid[0] + 400. / grid[0] - 2
            y = 800. * (i // grid[1]) / grid[1] + 400. / grid[1] + 2
            transform = ChainTransform([STTransform(translate=(x, y),
                                                    scale=(s, s, s)),
                                        self.rotation])
            mesh.transform = transform
            mesh.transforms.scene_transform = STTransform(scale=(1, 1, 0.01))

        self.show()

        self.timer = app.Timer(connect=self.rotate)
        self.timer.start(0.016)

    def rotate(self, event):
        # rotate with an irrational amount over each axis so there is no
        # periodicity
        self.rotation.rotate(0.2 ** 0.5, (1, 0, 0))
        self.rotation.rotate(0.3 ** 0.5, (0, 1, 0))
        self.rotation.rotate(0.5 ** 0.5, (0, 0, 1))
        self.update()

    def on_resize(self, event):
        # Set canvas viewport and reconfigure visual transforms to match.
        vp = (0, 0, self.physical_size[0], self.physical_size[1])
        self.context.set_viewport(*vp)

        for mesh in self.meshes:
            mesh.transforms.configure(canvas=self, viewport=vp)

    def on_draw(self, ev):
        gloo.set_viewport(0, 0, *self.physical_size)
        gloo.clear(color='black', depth=True)

        for mesh in self.meshes:
            mesh.draw()


if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        app.run()
