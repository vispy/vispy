# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Antigrain Geometry Fast Path Collection

This collection provides antialiased and accurate paths with caps and miter
joins. It consume x4 more memory than regular lines and is a bit slower, but
the quality of the output is worth the cost. Note that no control can be made
on miter joins which may result in some glitches on screen.
"""
import numpy as np
from ... import glsl
from ... import gloo
from . collection import Collection
from ..transforms import NullTransform


class AggFastPathCollection(Collection):
    """
    Antigrain Geometry Fast Path Collection

    This collection provides antialiased and accurate paths with caps and miter
    joins. It consume x4 more memory than regular lines and is a bit slower,
    but the quality of the output is worth the cost. Note that no control can
    be made on miter joins which may result in some glitches on screen.
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
        base_dtype = [('prev', (np.float32, 3), '!local', (0, 0, 0)),
                      ('curr', (np.float32, 3), '!local', (0, 0, 0)),
                      ('next', (np.float32, 3), '!local', (0, 0, 0)),
                      ('id', (np.float32, 1), '!local', 0),
                      ('color', (np.float32, 4), 'global', (0, 0, 0, 1)),
                      ('linewidth', (np.float32, 1), 'global', 1),
                      ('antialias', (np.float32, 1), 'global', 1),
                      ("viewport", (np.float32, 4), 'global', (0, 0, 512, 512))]  # noqa
        dtype = base_dtype
        if user_dtype:
            dtype.extend(user_dtype)

        if vertex is None:
            vertex = glsl.get('collections/agg-fast-path.vert')
        if transform is None:
            transform = NullTransform()
        self.transform = transform
        if fragment is None:
            fragment = glsl.get('collections/agg-fast-path.frag')

        Collection.__init__(self, dtype=dtype, itype=None,
                            mode="triangle_strip",
                            vertex=vertex, fragment=fragment, **kwargs)

        program = self._programs[0]
        program.vert['transform'] = self.transform

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

        color : list, array or 4-tuple
           Path color

        linewidth : list, array or float
           Path linewidth

        antialias : list, array or float
           Path antialias area
        """
        itemsize = int(itemsize or len(P))
        itemcount = len(P) // itemsize

        P = P.reshape(itemcount, itemsize, 3)
        if closed:
            V = np.empty((itemcount, itemsize + 3), dtype=self.vtype)
            # Apply default values on vertices
            for name in self.vtype.names:
                if name not in ['collection_index', 'prev', 'curr', 'next']:
                    V[name][1:-2] = kwargs.get(name, self._defaults[name])
            V['prev'][:, 2:-1] = P
            V['prev'][:, 1] = V['prev'][:, -2]
            V['curr'][:, 1:-2] = P
            V['curr'][:, -2] = V['curr'][:, 1]
            V['next'][:, 0:-3] = P
            V['next'][:, -3] = V['next'][:, 0]
            V['next'][:, -2] = V['next'][:, 1]
        else:
            V = np.empty((itemcount, itemsize + 2), dtype=self.vtype)
            # Apply default values on vertices
            for name in self.vtype.names:
                if name not in ['collection_index', 'prev', 'curr', 'next']:
                    V[name][1:-1] = kwargs.get(name, self._defaults[name])
            V['prev'][:, 2:] = P
            V['prev'][:, 1] = V['prev'][:, 2]
            V['curr'][:, 1:-1] = P
            V['next'][:, :-2] = P
            V['next'][:, -2] = V['next'][:, -3]

        V[:, 0] = V[:, 1]
        V[:, -1] = V[:, -2]
        V = V.ravel()
        V = np.repeat(V, 2, axis=0)
        V['id'] = np.tile([1, -1], len(V) // 2)
        if closed:
            V = V.reshape(itemcount, 2 * (itemsize + 3))
        else:
            V = V.reshape(itemcount, 2 * (itemsize + 2))
        V["id"][:, :2] = 2, -2
        V["id"][:, -2:] = 2, -2
        V = V.ravel()

        # Uniforms
        if self.utype:
            U = np.zeros(itemcount, dtype=self.utype)
            for name in self.utype.names:
                if name not in ["__unused__"]:
                    U[name] = kwargs.get(name, self._defaults[name])
        else:
            U = None

        Collection.append(self, vertices=V, uniforms=U,
                          itemsize=2 * (itemsize + 2 + closed))

    def bake(self, P, key='curr', closed=False, itemsize=None):
        """
        Given a path P, return the baked vertices as they should be copied in
        the collection if the path has already been appended.

        Examples
        --------
        >>> paths.append(P)
        >>> P *= 2
        >>> paths['prev'][0] = bake(P,'prev')
        >>> paths['curr'][0] = bake(P,'curr')
        >>> paths['next'][0] = bake(P,'next')

        """
        itemsize = itemsize or len(P)
        itemcount = len(P) / itemsize  # noqa
        n = itemsize

        if closed:
            idxs = np.arange(n + 3)
            if key == 'prev':
                idxs -= 2
                idxs[0], idxs[1], idxs[-1] = n - 1, n - 1, n - 1
            elif key == 'next':
                idxs[0], idxs[-3], idxs[-2], idxs[-1] = 1, 0, 1, 1
            else:
                idxs -= 1
                idxs[0], idxs[-1], idxs[n + 1] = 0, 0, 0
        else:
            idxs = np.arange(n + 2)
            if key == 'prev':
                idxs -= 2
                idxs[0], idxs[1], idxs[-1] = 0, 0, n - 2
            elif key == 'next':
                idxs[0], idxs[-1], idxs[-2] = 1, n - 1, n - 1
            else:
                idxs -= 1
                idxs[0], idxs[-1] = 0, n - 1
        idxs = np.repeat(idxs, 2)
        return P[idxs]

    def draw(self, mode="triangle_strip"):
        """Draw collection"""
        gloo.set_depth_mask(0)
        Collection.draw(self, mode)
        gloo.set_depth_mask(1)
