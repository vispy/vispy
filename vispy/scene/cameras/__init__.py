# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Cameras are responsible for determining which part of a scene is displayed
in a viewbox and for handling user input to change the view.

Several Camera subclasses are available to customize the projection of the 
scene such as 3D perspective and orthographic projections, 2D 
scale/translation, and other specialty cameras. A variety of user interaction
styles are available for each camera including arcball, turntable, 
first-person, and pan/zoom interactions.

Internally, Cameras work by setting the transform of a SubScene object such 
that a certain part of the scene is mapped to the bounding rectangle of the 
ViewBox.
"""
__all__ = ['ArcballCamera', 'BaseCamera', 'FlyCamera', 'MagnifyCamera',
           'Magnify1DCamera', 'PanZoomCamera', 'TurntableCamera']

from ._base import make_camera  # noqa
from .base_camera import BaseCamera  # noqa
from .panzoom import PanZoomCamera  # noqa
from .arcball import ArcballCamera  # noqa
from .turntable import TurntableCamera  # noqa
from .fly import FlyCamera  # noqa
from .magnify import MagnifyCamera, Magnify1DCamera  # noqa
