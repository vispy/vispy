# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
"""
Collections allow batch rendering of objects of the same type:

 - Points
 - Line segments
 - Polylines (paths)
 - Raw Triangles
 - Polygons

Each collection has several modes:

 - raw (point, segment, path, triangle, polygon): low-quality, very fast
 - agg (point, segment, path, polygon): high-quality, relatively fast
 - agg+ (path, polygon): very high quality, slow

Note: Storage of shared attributes requires non-clamped textures which is not
      the case on all graphic cards. This means such shared attributes must be
      normalized on CPU and scaled back on GPU (in shader code).
"""

from . path_collection import PathCollection  # noqa
from . point_collection import PointCollection  # noqa
from . polygon_collection import PolygonCollection  # noqa
from . segment_collection import SegmentCollection  # noqa
from . triangle_collection import TriangleCollection  # noqa
