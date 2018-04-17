# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Collections allow batch rendering of object of the same type:

 - Points
 - Line segments
 - Polylines (paths)
 - Raw Triangles
 - Polygons

Each collection has several modes:

 - raw (point, segment, path, triangle, polygon)
 - agg (point, segment, path, polygon)
 - agg+ (path, polygon)

Note: Storage of shared attributes requires non-clamped textures which is not
      the case on all graphic cards. This means such shared attributes must be
      normalized on CPU and scales back on GPU (in shader code).
"""

from . path_collection import PathCollection  # noqa
from . point_collection import PointCollection  # noqa
from . polygon_collection import PolygonCollection  # noqa
from . segment_collection import SegmentCollection  # noqa
from . triangle_collection import TriangleCollection  # noqa
