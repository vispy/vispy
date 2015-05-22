# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
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
from .cameras import (make_camera, BaseCamera, PanZoomCamera,  # noqa 
                      TurntableCamera, FlyCamera, ArcballCamera)  # noqa
from .magnify import MagnifyCamera, Magnify1DCamera  # noqa
