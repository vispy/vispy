# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
This module provides a library of Visual classes, which are drawable objects 
intended to encapsulate simple graphic objects such as lines, meshes, points, 
2D shapes, images, text, etc.

These classes define only the OpenGL machinery and connot be used directly in
a scenegraph. For scenegraph use, see the complementary Visual+Node classes 
defined in vispy.scene.
"""

__all__ = ['Visual', 'Cube', 'Ellipse', 'GridLines', 'Image', 'Line',
           'LinePlot', 'Markers', 'marker_types', 'Mesh', 'Polygon',
           'Rectangle', 'RegularPolygon', 'SurfacePlot', 'Text', 'XYZAxis']

from .node import Node  # noqa
from .visual import Visual  # noqa
from .line import Line  # noqa
from .markers import Markers, marker_types  # noqa
from .mesh import Mesh  # noqa
from .image import Image  # noqa
from .polygon import Polygon  # noqa
from .ellipse import Ellipse  # noqa
from .regular_polygon import RegularPolygon  # noqa
from .rectangle import Rectangle  # noqa
from .text import Text  # noqa
from .gridlines import GridLines  # noqa
from .surface_plot import SurfacePlot  # noqa
from .isosurface import Isosurface  # noqa
from .isocurve import Isocurve  # noqa
from .xyz_axis import XYZAxis  # noqa
from .line_plot import LinePlot  # noqa
from .cube import Cube  # noqa
