# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Antigrain Geometry Segment Collection

This collection provides antialiased and accurate segments with caps. It
consume x2 more memory than regular lines and is a bit slower, but the quality
of the output is worth the cost.
"""
import numpy as np
from ... import glsl
from . collection import Collection
from ..transforms import NullTransform


class AggSegmentCollection(Collection):

    """
    Antigrain Geometry Segment Collection

    This collection provides antialiased and accurate segments with caps. It
    consume x2 more memory than regular lines and is a bit slower, but the
    quality of the output is worth the cost.
    """

    def __init__(self, user_dtype=None, transform=None,
                 vertex=None, fragment=None, **kwargs):
        """
        Initialize the collection.

        Parameters
        ----------

        user_dtype: list
            The base dtype can be completed (appended) by the used_dtype. It
            only make sense if user also provide vertex and/or fragment shaders

        transform : string
            GLSL Transform code defining the vec4 transform(vec3) function

        vertex: string
            Vertex shader code

        fragment: string
            Fragment  shader code

        caps : string
            'local', 'shared' or 'global'

        color : string
            'local', 'shared' or 'global'

        linewidth : string
            'local', 'shared' or 'global'

        antialias : string
            'local', 'shared' or 'global'
        """

        base_dtype = [('P0',        (np.float32, 3), '!local', (0, 0, 0)),
                      ('P1',        (np.float32, 3), '!local', (0, 0, 0)),
                      ('index',     (np.float32, 1), '!local', 0),
                      ('color',     (np.float32, 4), 'shared', (0, 0, 0, 1)),
                      ('linewidth', (np.float32, 1), 'shared', 1),
                      ('antialias', (np.float32, 1), 'shared', 1),
                      ('viewport',  (np.float32, 4), 'global', (0, 0, 512, 512))]  # noqa

        dtype = base_dtype
        if user_dtype:
            dtype.extend(user_dtype)

        if vertex is None:
            vertex = glsl.get('collections/agg-segment.vert')
        if transform is None:
            transform = NullTransform()
        self.transform = transform        
        if fragment is None:
            fragment = glsl.get('collections/agg-segment.frag')

        Collection.__init__(self, dtype=dtype, itype=np.uint32,
                            mode="triangles",
                            vertex=vertex, fragment=fragment, **kwargs)
        self._programs[0].vert['transform'] = self.transform

    def append(self, P0, P1, itemsize=None, **kwargs):
        """
        Append a new set of segments to the collection.

        For kwargs argument, n is the number of vertices (local) or the number
        of item (shared)

        Parameters
        ----------

        P : np.array
            Vertices positions of the path(s) to be added

        itemsize: int or None
            Size of an individual path

        caps : list, array or 2-tuple
           Path start /end cap

        color : list, array or 4-tuple
           Path color

        linewidth : list, array or float
           Path linewidth

        antialias : list, array or float
           Path antialias area
        """

        itemsize = itemsize or 1
        itemcount = len(P0) // itemsize

        V = np.empty(itemcount, dtype=self.vtype)

        # Apply default values on vertices
        for name in self.vtype.names:
            if name not in ['collection_index', 'P0', 'P1', 'index']:
                V[name] = kwargs.get(name, self._defaults[name])

        V['P0'] = P0
        V['P1'] = P1
        V = V.repeat(4, axis=0)
        V['index'] = np.resize([0, 1, 2, 3], 4 * itemcount * itemsize)

        I = np.ones((itemcount, 6), dtype=int)
        I[:] = 0, 1, 2, 0, 2, 3
        I[:] += 4 * np.arange(itemcount)[:, np.newaxis]
        I = I.ravel()

        # Uniforms
        if self.utype:
            U = np.zeros(itemcount, dtype=self.utype)
            for name in self.utype.names:
                if name not in ["__unused__"]:
                    U[name] = kwargs.get(name, self._defaults[name])
        else:
            U = None

        Collection.append(
            self, vertices=V, uniforms=U, indices=I, itemsize=4 * itemcount)
