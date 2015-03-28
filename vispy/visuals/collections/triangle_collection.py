# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

from . raw_triangle_collection import RawTriangleCollection


def TriangleCollection(mode="raw", *args, **kwargs):
    """
    mode: string
      - "raw"  (speed: fastest, size: small,   output: ugly)
      - "agg"  (speed: fast,    size: small,   output: beautiful)
    """

    return RawTriangleCollection(*args, **kwargs)
