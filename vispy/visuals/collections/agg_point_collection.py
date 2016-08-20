# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Antigrain Geometry Point Collection

This collection provides fast points. Output quality is perfect.
"""
from ... import glsl
from . raw_point_collection import RawPointCollection


class AggPointCollection(RawPointCollection):

    """
    Antigrain Geometry Point Collection

    This collection provides fast points. Output quality is perfect.
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

        vertex: string
            Vertex shader code

        fragment: string
            Fragment  shader code

        transform : Transform instance
            Used to define the GLSL transform(vec4) function

        color : string
            'local', 'shared' or 'global'
        """
        if vertex is None:
            vertex = glsl.get("collections/agg-point.vert")
        if fragment is None:
            fragment = glsl.get("collections/agg-point.frag")

        RawPointCollection.__init__(self, user_dtype=user_dtype,
                                    transform=transform,
                                    vertex=vertex, fragment=fragment, **kwargs)
