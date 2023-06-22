# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
The vispy.scene subpackage provides high-level, flexible, and easy to use
functionality for creating scenes composed of multiple visual objects.

Overview
--------

Scenegraphs are a commonly used system for describing a scene as a
hierarchy of visual objects. Users need only create these visual objects and
specify their location in the scene, and the scenegraph system will
automatically draw the entire scene whenever an update is required.

Using the vispy scenegraph requires only a few steps:

1. Create a SceneCanvas to display the scene. This object has a `scene`
   property that is the top-level Node in the scene.
2. Create one or more Node instances (see vispy.scene.visuals)
3. Add these Node instances to the scene by making them children of
   canvas.scene, or children of other nodes that are already in the scene.


For more information see:

* complete scenegraph documentation
* scene examples
* scene API reference

"""

from .visuals import *  # noqa
from .cameras import *  # noqa
from ..visuals.transforms import *  # noqa
from .widgets import *  # noqa
from .canvas import SceneCanvas  # noqa
from . import visuals  # noqa
from ..visuals import transforms  # noqa
from ..visuals import filters  # noqa
from . import widgets  # noqa
from . import cameras  # noqa
from .node import Node  # noqa
