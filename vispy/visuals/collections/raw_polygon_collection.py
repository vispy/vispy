# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import numpy as np
from ... import glsl
from . collection import Collection
from ..transforms import NullTransform
from ...geometry import triangulate


class RawPolygonCollection(Collection):

    def __init__(self, user_dtype=None, transform=None,
                 vertex=None, fragment=None, **kwargs):

        base_dtype = [('position', (np.float32, 3), '!local', (0, 0, 0)),
                      ('color',    (np.float32, 4), 'local',  (0, 0, 0, 1))]

        dtype = base_dtype
        if user_dtype:
            dtype.extend(user_dtype)

        if vertex is None:
            vertex = glsl.get('collections/raw-triangle.vert')
        if transform is None:
            transform = NullTransform()
        self.transform = transform        
        if fragment is None:
            fragment = glsl.get('collections/raw-triangle.frag')

        Collection.__init__(self, dtype=dtype, itype=np.uint32,  # 16 for WebGL
                            mode="triangles",
                            vertex=vertex, fragment=fragment, **kwargs)

        # Set hooks if necessary
        program = self._programs[0]
        program.vert['transform'] = self.transform

    def append(self, points, **kwargs):
        """
        Append a new set of vertices to the collection.

        For kwargs argument, n is the number of vertices (local) or the number
        of item (shared)

        Parameters
        ----------

        points : np.array
            Vertices composing the triangles

        color : list, array or 4-tuple
           Path color
        """

        vertices, indices = triangulate(points)
        itemsize = len(vertices)
        itemcount = 1

        V = np.empty(itemcount * itemsize, dtype=self.vtype)
        for name in self.vtype.names:
            if name not in ['collection_index', 'position']:
                V[name] = kwargs.get(name, self._defaults[name])
        V["position"] = vertices

        # Uniforms
        if self.utype:
            U = np.zeros(itemcount, dtype=self.utype)
            for name in self.utype.names:
                if name not in ["__unused__"]:
                    U[name] = kwargs.get(name, self._defaults[name])
        else:
            U = None

        I = np.array(indices).ravel()
        Collection.append(self, vertices=V, uniforms=U, indices=I,
                          itemsize=itemsize)
