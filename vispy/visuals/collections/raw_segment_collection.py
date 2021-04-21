# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Raw Segment Collection

This collection provides fast raw (& ugly) line segments.
"""
import numpy as np
from ... import glsl
from . collection import Collection
from ..transforms import NullTransform


class RawSegmentCollection(Collection):
    """
    Raw Segment Collection

    This collection provides fast raw (& ugly) line segments.
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

        color : string
            'local', 'shared' or 'global'
        """
        base_dtype = [("position", (np.float32, 3), "!local", (0, 0, 0)),
                      ("color", (np.float32, 4), "global", (0, 0, 0, 1)),
                      ("viewport", (np.float32, 4), "global", (0, 0, 512, 512))
                      ]

        dtype = base_dtype
        if user_dtype:
            dtype.extend(user_dtype)

        if vertex is None:
            vertex = glsl.get('collections/raw-segment.vert')
        if transform is None:
            transform = NullTransform()
        self.transform = transform        
        if fragment is None:
            fragment = glsl.get('collections/raw-segment.frag')

        Collection.__init__(self, dtype=dtype, itype=None, mode='lines',
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

        closed: bool
            Whether path(s) is/are closed

        itemsize: int or None
            Size of an individual path

        color : list, array or 4-tuple
           Path color
        """
        itemsize = itemsize or 1
        itemcount = len(P0) / itemsize

        V = np.empty(itemcount, dtype=self.vtype)

        # Apply default values on vertices
        for name in self.vtype.names:
            if name not in ['collection_index', 'P']:
                V[name] = kwargs.get(name, self._defaults[name])

        V = np.repeat(V, 2, axis=0)
        V['P'][0::2] = P0
        V['P'][1::2] = P1

        # Uniforms
        if self.utype:
            U = np.zeros(itemcount, dtype=self.utype)
            for name in self.utype.names:
                if name not in ["__unused__"]:
                    U[name] = kwargs.get(name, self._defaults[name])
        else:
            U = None

        Collection.append(self, vertices=V, uniforms=U, itemsize=itemsize)
