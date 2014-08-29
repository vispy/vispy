# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
The vispy.scene.visuals namespace provides a wide range of visuals.
A Visual is an Entity that displays something.

Visuals do not have to be used in a scenegraph per se; they can also
be used stand-alone e.g. from a vispy.app.Canvas, or using Glut.

This module provides a library of drawable objects that are intended to
encapsulate simple graphic objects such as lines, meshes, points, 2D shapes,
images, text, etc.
"""

__all__ = ['Visual', 'Ellipse', 'GridLines', 'Image', 'Line', 'LinePlot',
           'Markers', 'marker_types', 'Mesh', 'Polygon', 'Rectangle',
           'RegularPolygon', 'SurfacePlot', 'Text', 'XYZAxis']

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
