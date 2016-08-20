# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
This module provides a library of Visual classes, which are drawable objects
intended to encapsulate simple graphic objects such as lines, meshes, points,
2D shapes, images, text, etc.

These classes define only the OpenGL machinery and connot be used directly in
a scenegraph. For scenegraph use, see the complementary Visual+Node classes
defined in vispy.scene.
"""

from .axis import AxisVisual  # noqa
from .box import BoxVisual  # noqa
from .cube import CubeVisual  # noqa
from .ellipse import EllipseVisual  # noqa
from .gridlines import GridLinesVisual  # noqa
from .image import ImageVisual  # noqa
from .gridmesh import GridMeshVisual  # noqa
from .histogram import HistogramVisual  # noqa
from .infinite_line import InfiniteLineVisual  # noqa
from .isocurve import IsocurveVisual  # noqa
from .isoline import IsolineVisual  # noqa
from .isosurface import IsosurfaceVisual  # noqa
from .line import LineVisual, ArrowVisual  # noqa
from .linear_region import LinearRegionVisual  # noqa
from .line_plot import LinePlotVisual  # noqa
from .markers import MarkersVisual, marker_types  # noqa
from .mesh import MeshVisual  # noqa
from .plane import PlaneVisual  # noqa
from .polygon import PolygonVisual  # noqa
from .rectangle import RectangleVisual  # noqa
from .regular_polygon import RegularPolygonVisual  # noqa
from .scrolling_lines import ScrollingLinesVisual  # noqa
from .spectrogram import SpectrogramVisual  # noqa
from .sphere import SphereVisual  # noqa
from .surface_plot import SurfacePlotVisual  # noqa
from .text import TextVisual  # noqa
from .tube import TubeVisual  # noqa
from .visual import BaseVisual, Visual, CompoundVisual  # noqa
from .volume import VolumeVisual  # noqa
from .xyz_axis import XYZAxisVisual  # noqa
from .border import _BorderVisual  # noqa
from .colorbar import ColorBarVisual  # noqa
from .graphs import GraphVisual  # noqa
