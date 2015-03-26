# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
""" """
from . raw_polygon_collection import RawPolygonCollection
#from . agg_polygon_collection import AggPolygonCollection
#from . agg_fast_polygon_collection import AggPolygonCollection


def PolygonCollection(mode="raw", *args, **kwargs):
    """
    mode: string
      - "raw"   (speed: fastest, size: small, output: ugly, no dash, no
                 thickness)
      - "agg"   (speed: medium,  size: medium output: nice, some flaws, no
                 dash)
      - "agg+"  (speed: slow, size: big, output: perfect, no dash)
    """

    # if mode == "raw":
    return RawPolygonCollection(*args, **kwargs)
    # elif mode == "agg":
    #    return AggFastPolygonCollection(*args, **kwargs)
    # return AggPolygonCollection(*args, **kwargs)
