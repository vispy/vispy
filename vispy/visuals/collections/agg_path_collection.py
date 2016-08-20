# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Antigrain Geometry Path Collection

This collection provides antialiased and accurate paths with caps and joins. It
is memory hungry (x8) and slow (x.25) so it is to be used sparingly, mainly for
thick paths where quality is critical.
"""
import numpy as np
from ... import glsl
from ...gloo import gl
from . collection import Collection
from ..transforms import NullTransform


class AggPathCollection(Collection):

    """
    Antigrain Geometry Path Collection

    This collection provides antialiased and accurate paths with caps and
    joins. It is memory hungry (x8) and slow (x.25) so it is to be used
    sparingly, mainly for thick paths where quality is critical.
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

        transform : Transform instance
            Used to define the transform(vec4) function

        vertex: string
            Vertex shader code

        fragment: string
            Fragment  shader code

        caps : string
            'local', 'shared' or 'global'

        join : string
            'local', 'shared' or 'global'

        color : string
            'local', 'shared' or 'global'

        miter_limit : string
            'local', 'shared' or 'global'

        linewidth : string
            'local', 'shared' or 'global'

        antialias : string
            'local', 'shared' or 'global'
        """

        base_dtype = [('p0',         (np.float32, 3), '!local', (0, 0, 0)),
                      ('p1',         (np.float32, 3), '!local', (0, 0, 0)),
                      ('p2',         (np.float32, 3), '!local', (0, 0, 0)),
                      ('p3',         (np.float32, 3), '!local', (0, 0, 0)),
                      ('uv',         (np.float32, 2), '!local', (0, 0)),

                      ('caps',       (np.float32, 2), 'global', (0, 0)),
                      ('join',       (np.float32, 1), 'global', 0),
                      ('color',      (np.float32, 4), 'global', (0, 0, 0, 1)),
                      ('miter_limit', (np.float32, 1), 'global', 4),
                      ('linewidth',  (np.float32, 1), 'global', 1),
                      ('antialias',  (np.float32, 1), 'global', 1),
                      ('viewport',   (np.float32, 4), 'global', (0, 0, 512, 512))]  # noqa

        dtype = base_dtype
        if user_dtype:
            dtype.extend(user_dtype)

        if vertex is None:
            vertex = glsl.get('collections/agg-path.vert')
        if transform is None:
            transform = NullTransform()
        self.transform = transform        
        if fragment is None:
            fragment = glsl.get('collections/agg-path.frag')

        Collection.__init__(self, dtype=dtype, itype=np.uint32,  # 16 for WebGL
                            mode="triangles",
                            vertex=vertex, fragment=fragment, **kwargs)
        self._programs[0].vert['transform'] = self.transform

    def append(self, P, closed=False, itemsize=None, **kwargs):
        """
        Append a new set of vertices to the collection.

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

        caps : list, array or 2-tuple
           Path start /end cap

        join : list, array or float
           path segment join

        color : list, array or 4-tuple
           Path color

        miter_limit : list, array or float
           Miter limit for join

        linewidth : list, array or float
           Path linewidth

        antialias : list, array or float
           Path antialias area
        """

        itemsize = itemsize or len(P)
        itemcount = len(P) / itemsize

        # Computes the adjacency information
        n, p = len(P), P.shape[-1]
        Z = np.tile(P, 2).reshape(2 * len(P), p)
        V = np.empty(n, dtype=self.vtype)

        V['p0'][1:-1] = Z[0::2][:-2]
        V['p1'][:-1] = Z[1::2][:-1]
        V['p2'][:-1] = Z[1::2][+1:]
        V['p3'][:-2] = Z[0::2][+2:]

        # Apply default values on vertices
        for name in self.vtype.names:
            if name not in ['collection_index', 'p0', 'p1', 'p2', 'p3']:
                V[name] = kwargs.get(name, self._defaults[name])

        # Extract relevant segments only
        V = (V.reshape(n / itemsize, itemsize)[:, :-1])
        if closed:
            V['p0'][:, 0] = V['p2'][:, -1]
            V['p3'][:, -1] = V['p1'][:, 0]
        else:
            V['p0'][:, 0] = V['p1'][:, 0]
            V['p3'][:, -1] = V['p2'][:, -1]
        V = V.ravel()

        # Quadruple each point (we're using 2 triangles / segment)
        # No shared vertices between segment because of joins
        V = np.repeat(V, 4, axis=0).reshape((len(V), 4))
        V['uv'] = (-1, -1), (-1, +1), (+1, -1), (+1, +1)
        V = V.ravel()

        n = itemsize
        if closed:
            # uint16 for WebGL
            I = np.resize(
                np.array([0, 1, 2, 1, 2, 3], dtype=np.uint32), n * 2 * 3)
            I += np.repeat(4 * np.arange(n, dtype=np.uint32), 6)
            I[-6:] = 4 * n - 6, 4 * n - 5, 0, 4 * n - 5, 0, 1
        else:
            I = np.resize(
                np.array([0, 1, 2, 1, 2, 3], dtype=np.uint32), (n - 1) * 2 * 3)
            I += np.repeat(4 * np.arange(n - 1, dtype=np.uint32), 6)
        I = I.ravel()

        # Uniforms
        if self.utype:
            U = np.zeros(itemcount, dtype=self.utype)
            for name in self.utype.names:
                if name not in ["__unused__"]:
                    U[name] = kwargs.get(name, self._defaults[name])
        else:
            U = None

        Collection.append(self, vertices=V, uniforms=U,
                          indices=I, itemsize=itemsize * 4 - 4)

    def draw(self, mode="triangles"):
        """ Draw collection """

        gl.glDepthMask(0)
        Collection.draw(self, mode)
        gl.glDepthMask(1)
