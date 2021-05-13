# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
from . raw_path_collection import RawPathCollection
from . agg_path_collection import AggPathCollection
from . agg_fast_path_collection import AggFastPathCollection


def PathCollection(mode="agg", *args, **kwargs):
    """
    mode: string
      - "raw"   (speed: fastest, size: small, output: ugly, no dash,
                 no thickness)
      - "agg"   (speed: medium, size: medium output: nice, some flaws, no dash)
      - "agg+"  (speed: slow, size: big, output: perfect, no dash)
    """
    if mode == "raw":
        return RawPathCollection(*args, **kwargs)
    elif mode == "agg+":
        return AggPathCollection(*args, **kwargs)
    return AggFastPathCollection(*args, **kwargs)
